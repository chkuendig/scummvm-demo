#!/usr/bin/env python3
"""ScummVM Game Downloader and Uploader."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

from helper_gsheet import (
    CombinedEntry,
    build_unified_demo_catalog,
    compute_relative_path,
    load_metadata,
    merge_entry,
    normalize_download_url,
    validate_remote_folders,
)

class GameDownloader:
    def __init__(self, download_dir: str = "games", scp_server: Optional[str] = None, scp_path: Optional[str] = None, scp_port: Optional[int] = None):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.scp_server = scp_server
        self.scp_path = scp_path
        self.scp_port = scp_port

        self.catalog: Dict[str, CombinedEntry] = {}
        self.metadata_by_path: Dict[str, Dict[str, object]] = {}
        self.alias_map: Dict[str, str] = {}
        self.merged_metadata_by_path: Dict[str, Dict[str, object]] = {}
        self.processed_games_metadata: List[Dict[str, object]] = []

    # --- Catalog helpers -------------------------------------------------

    def refresh_catalog(self, metadata_path: Path) -> None:
        # Use the unified catalog builder which includes all debug output
        self.catalog = build_unified_demo_catalog(metadata_path)
        self.metadata_by_path = load_metadata(metadata_path)

        self.alias_map.clear()
        self.merged_metadata_by_path.clear()
        for relative_path, entry in self.catalog.items():
            merged_entry, notes = merge_entry(relative_path, entry.metadata, entry.demo_row)
            self.merged_metadata_by_path[relative_path] = merged_entry
            for note in notes:
                print(f"Warning: {relative_path}: {note}", file=sys.stderr)
            self._register_alias(relative_path, entry, merged_entry)

    def _register_alias(self, relative_path: str, entry: CombinedEntry, merged_entry: Dict[str, object]) -> None:
        def add_alias(value: Optional[str]) -> None:
            if not value:
                return
            self.alias_map.setdefault(value.lower(), relative_path)

        add_alias(relative_path)
        add_alias(relative_path.lower())
        if entry.game_id:
            add_alias(entry.game_id)
            short_id = entry.game_id.split(":")[-1]
            add_alias(short_id)
        if entry.sheet_download_url:
            add_alias(entry.sheet_download_url)
        if entry.sheet_download_url_relative:
            add_alias(entry.sheet_download_url_relative)
        metadata_download = str((entry.metadata or {}).get("download_url") or "").strip()
        if metadata_download:
            add_alias(metadata_download)
            add_alias(normalize_download_url(metadata_download))
        merged_download = str(merged_entry.get("download_url") or "").strip()
        if merged_download:
            add_alias(merged_download)
            add_alias(normalize_download_url(merged_download))

    def resolve_requested_targets(self, requested: Sequence[str]) -> List[str]:
        if not requested:
            # Return only entries that should be synced (not marked with skip=true)
            syncable = [path for path, entry in self.catalog.items() if entry.should_sync]
            return sorted(syncable)

        resolved: List[str] = []
        for token in requested:
            candidate = (token or "").strip()
            if not candidate:
                continue

            lookup_keys = [candidate.lower()]
            rel_candidate = compute_relative_path(candidate)
            if rel_candidate:
                lookup_keys.append(rel_candidate.lower())

            if candidate.startswith("http"):
                parsed_relative = compute_relative_path(candidate)
                if parsed_relative:
                    lookup_keys.append(parsed_relative.lower())

            resolved_relative: Optional[str] = None
            for key in lookup_keys:
                resolved_relative = self.alias_map.get(key)
                if resolved_relative:
                    break

            if not resolved_relative:
                raise ValueError(f"Unknown game identifier: {token}")

            if resolved_relative not in resolved:
                resolved.append(resolved_relative)

        return resolved

    def _select_download_url(self, entry: CombinedEntry) -> Optional[str]:
        candidate = entry.sheet_download_url
        if not candidate and entry.metadata:
            candidate = str(entry.metadata.get("download_url") or "").strip() or None
        if not candidate:
            return None
        if candidate.startswith("http://") or candidate.startswith("https://"):
            return candidate
        if candidate.startswith("/"):
            return f"https://downloads.scummvm.org{candidate}"
        return candidate

    # --- Output helpers --------------------------------------------------

    def generate_processed_games_json(self) -> None:
        output_file = Path.cwd() / "games.json"
        sorted_games = sorted(self.processed_games_metadata, key=lambda item: (str(item.get("id", "")).lower(), item["relative_path"].lower()))
        with open(output_file, "w", encoding="utf-8") as handle:
            json.dump(sorted_games, handle, indent=2, ensure_ascii=False)
        self._print(f"Generated games.json with {len(sorted_games)} processed games")

    # --- Logging helpers -------------------------------------------------

    def _temp_print(self, message: str, file=sys.stderr) -> None:
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80
        padded_message = message.ljust(terminal_width)
        print(padded_message, end="\r", flush=True, file=file)

    def _print(self, message: str, file=sys.stderr) -> None:
        try:
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80
        padded_message = message.ljust(terminal_width)
        print(padded_message, file=file)

    # --- SSH helpers -----------------------------------------------------

    def _build_ssh_command(self, base_command: str = "ssh"):
        cmd: List[str] = []
        env = os.environ.copy()
        control_path = "/tmp/scummvm-ssh-%r@%h:%p"

        ssh_password = os.environ.get("SSH_PASSWORD")
        if ssh_password:
            cmd.extend(["sshpass", "-e", base_command])
            env["SSHPASS"] = ssh_password
        else:
            cmd.append(base_command)

        ssh_key = os.environ.get("SSH_KEY_PATH")
        if ssh_key and not ssh_password:
            cmd.extend(["-i", ssh_key])

        if self.scp_port:
            if base_command == "scp":
                cmd.extend(["-P", str(self.scp_port)])
            else:
                cmd.extend(["-p", str(self.scp_port)])

        cmd.extend(["-o", "ControlMaster=auto", "-o", f"ControlPath={control_path}", "-o", "ControlPersist=600"])

        if ssh_password:
            cmd.extend(["-o", "StrictHostKeyChecking=no"])
        else:
            cmd.extend(["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no"])

        return cmd, env

    def _build_controlpath_ssh_command(self, base_command: str = "ssh") -> List[str]:
        cmd = [base_command]
        control_path = "/tmp/scummvm-ssh-%r@%h:%p"

        if self.scp_port:
            if base_command == "scp":
                cmd.extend(["-P", str(self.scp_port)])
            else:
                cmd.extend(["-p", str(self.scp_port)])

        cmd.extend(["-o", f"ControlPath={control_path}"])
        return cmd

    def open_connection(self) -> None:
        ssh_cmd, env = self._build_ssh_command()
        ssh_pos = next((i for i, arg in enumerate(ssh_cmd) if arg in {"ssh", "scp"}), 0)
        ssh_cmd.insert(ssh_pos + 1, "-MNf")
        ssh_cmd.append(f"{self.scp_server}")
        subprocess.run(ssh_cmd, check=True, env=env)
        self._temp_print("Opened SSH connection")

    def close_connection(self) -> None:
        control_path = "/tmp/scummvm-ssh-%r@%h:%p"
        close_cmd = ["ssh", "-O", "exit", "-o", f"ControlPath={control_path}", f"{self.scp_server}"]
        result = subprocess.run(close_cmd, check=False, capture_output=True)
        if result.returncode == 0:
            self._temp_print("Closed SSH connection")
        elif result.returncode == 255:
            self._temp_print("SSH connection already closed")
        else:
            stderr_output = result.stderr.decode("utf-8", errors="ignore").strip()
            self._print(f"Warning: Could not close SSH connection (exit code {result.returncode}): {stderr_output}")

    def get_remote_folders(self) -> Set[str]:
        if not self.scp_server or not self.scp_path:
            return set()

        ssh_cmd = self._build_controlpath_ssh_command()
        env = os.environ.copy()
        ssh_cmd.extend([self.scp_server, f'ls -1 "{self.scp_path}"'])

        result = subprocess.run(ssh_cmd, capture_output=True, check=False, env=env, timeout=30, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Remote command failed: {result.stderr.strip()}")

        folders: Set[str] = set()
        for line in result.stdout.strip().splitlines():
            entry = line.strip()
            if not entry:
                continue
            test_cmd = self._build_controlpath_ssh_command()
            test_cmd.extend([self.scp_server, f'test -d "{self.scp_path}/{entry}"'])
            test_result = subprocess.run(test_cmd, capture_output=True, check=False, env=env, timeout=10)
            if test_result.returncode == 0:
                folders.add(entry)
        return folders

    def folder_exists_on_remote(self, folder_name: str, remote_folders_set: Optional[Set[str]] = None) -> bool:
        if not self.scp_server or not self.scp_path:
            return False

        if remote_folders_set is not None:
            if folder_name in remote_folders_set:
                remote_folders_set.remove(folder_name)
                return True
            return False

        ssh_cmd = self._build_controlpath_ssh_command()
        env = os.environ.copy()
        ssh_cmd.extend([self.scp_server, f'test -d "{self.scp_path}/{folder_name}"'])

        result = subprocess.run(ssh_cmd, capture_output=True, check=False, env=env, timeout=30)
        if result.returncode in (0, 1):
            return result.returncode == 0

        stderr_output = result.stderr.decode("utf-8", errors="ignore").strip()
        if result.returncode == 255:
            raise RuntimeError(f"Failed to connect to remote server: {stderr_output}")
        raise RuntimeError(f"Remote command failed: {stderr_output}")

    # --- File transfer helpers ------------------------------------------

    def download_file(self, url: str, filename: str) -> Path:
        filepath = self.download_dir / filename
        temp_filepath = self.download_dir / f"{filename}.downloading"

        parsed_url = urllib.parse.urlparse(url)
        encoded_path = urllib.parse.quote(parsed_url.path, safe="/")
        encoded_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, encoded_path, parsed_url.params, parsed_url.query, parsed_url.fragment))

        self._temp_print(f"Downloading {encoded_url}")
        urllib.request.urlretrieve(encoded_url, temp_filepath)
        temp_filepath.rename(filepath)
        self._temp_print(f"Download completed: {filename}")
        return filepath

    def extract_zip(self, zip_path: Path) -> Path:
        zip_path = Path(zip_path)
        extract_dir = self.download_dir / zip_path.stem
        if extract_dir.exists():
            self._print(f"Directory {extract_dir} already exists, skipping extraction")
            return extract_dir

        self._temp_print(f"Extracting {zip_path} to {extract_dir}")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        zip_path.unlink()
        self._temp_print(f"Removed {zip_path}")
        return extract_dir

    def upload_folder(self, folder_path: Path) -> bool:
        if not self.scp_server or not self.scp_path:
            self._print("No SCP server configured, skipping upload")
            return False

        folder_path = Path(folder_path)
        folder_name = folder_path.name
        temp_name = f"{folder_name}.uploading"

        cleanup_cmd = self._build_controlpath_ssh_command()
        env = os.environ.copy()
        cleanup_cmd.extend([self.scp_server, f'rm -rf "{self.scp_path}/{temp_name}"'])
        subprocess.run(cleanup_cmd, check=False, env=env, capture_output=True)

        scp_cmd = self._build_controlpath_ssh_command("scp")
        scp_cmd.append("-r")
        scp_cmd.extend([str(folder_path), f"{self.scp_server}:{self.scp_path}/{temp_name}"])
        subprocess.run(scp_cmd, check=True, env=env)

        ssh_cmd = self._build_controlpath_ssh_command()
        ssh_cmd.extend([self.scp_server, f'mv "{self.scp_path}/{temp_name}" "{self.scp_path}/{folder_name}"'])
        subprocess.run(ssh_cmd, check=True, env=env)

        self._print(f"\033[1;32mGame {folder_name} successfully uploaded\033[0m")
        return True

    def build_http_index(self) -> None:
        if not self.scp_server or not self.scp_path:
            return

        self._temp_print("Getting remote directory listing...")
        ssh_cmd = self._build_controlpath_ssh_command()
        env = os.environ.copy()
        find_command = f'cd "{self.scp_path}" && find . -printf "%y %s %p\\n" 2>/dev/null'
        ssh_cmd.extend([self.scp_server, find_command])
        result = subprocess.run(ssh_cmd, capture_output=True, check=False, env=env, text=True)
        if result.returncode != 0:
            self._print(f"Warning: Could not get remote directory listing: {result.stderr}")
            return

        directories: Set[str] = set()
        existing_index_dirs: Set[str] = set()
        files_with_size: List[Tuple[str, int]] = []

        for raw_line in result.stdout.strip().splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                entry_type, size_str, path_value = line.split(" ", 2)
            except ValueError:
                continue

            if path_value.startswith("./"):
                path_value = path_value[2:]

            normalized_path = path_value
            if normalized_path == ".":
                normalized_path = ""

            path_parts = [part for part in normalized_path.split("/") if part]
            if any(part.startswith(".") for part in path_parts):
                continue

            if entry_type == "d":
                directories.add(normalized_path)
            elif entry_type == "f":
                try:
                    size = int(size_str)
                except ValueError:
                    continue

                parent_dir = normalized_path.rsplit("/", 1)[0] if "/" in normalized_path else ""
                filename = normalized_path.rsplit("/", 1)[-1]
                if filename == "index.json":
                    existing_index_dirs.add(parent_dir)
                    continue

                if normalized_path:
                    files_with_size.append((normalized_path, size))

        directories.add("")  # Ensure root is tracked

        file_tree: Dict[str, object] = {}
        for filepath, size in files_with_size:
            parts = filepath.split("/")
            current = file_tree
            for part in parts[:-1]:
                current = current.setdefault(part, {})  # type: ignore[assignment]
            current[parts[-1]] = size  # type: ignore[index]

        for directory in sorted(dir_name for dir_name in directories if dir_name):
            current = file_tree
            for part in directory.split("/"):
                current = current.setdefault(part, {})  # type: ignore[assignment]

        dirs_to_update = {directory for directory in directories if directory not in existing_index_dirs}

        if not dirs_to_update:
            self._print("All index.json files already present")
            return

        self._generate_index_files(file_tree, self.scp_path, dirs_to_update)
        self._temp_print("HTTP index built successfully")

    def _generate_index_files(
        self,
        tree: Dict[str, object],
        remote_path: str,
        dirs_to_update: Set[str],
        current_path: str = "",
    ) -> None:
        remote_index_path = f"{remote_path}/{current_path}/index.json" if current_path else f"{remote_path}/index.json"
        if current_path in dirs_to_update:
            simplified_tree = {key: {} if isinstance(value, dict) else value for key, value in tree.items()}
            temp_index_file = self.download_dir / "temp_index.json"
            with open(temp_index_file, "w", encoding="utf-8") as handle:
                json.dump(simplified_tree, handle, indent=2, ensure_ascii=False)
            scp_cmd = self._build_controlpath_ssh_command("scp")
            env = os.environ.copy()
            scp_cmd.extend([str(temp_index_file), f"{self.scp_server}:{remote_index_path}"])
            subprocess.run(scp_cmd, check=True, env=env)
            temp_index_file.unlink()
            printable_path = current_path or "."
            self._print(f"Created index.json in {printable_path}")
            dirs_to_update.discard(current_path)

        for key, value in tree.items():
            if isinstance(value, dict):
                subdir_path = f"{current_path}/{key}" if current_path else key
                self._generate_index_files(value, remote_path, dirs_to_update, subdir_path)

    # --- Processing ------------------------------------------------------

    def download_and_process_games(self, requested_ids: Sequence[str], max_transfers: Optional[int] = None) -> None:
        targets = self.resolve_requested_targets(requested_ids)
        self.processed_games_metadata = []

        try:
            remote_folders_snapshot = self.get_remote_folders()
            self._print(f"Found {len(remote_folders_snapshot)} folders on remote server")
        except RuntimeError as exc:
            self._print(f"Error getting remote folders: {exc}")
            return

        remote_folders_remaining = set(remote_folders_snapshot)
        remote_folders_for_validation = set(remote_folders_snapshot)

        transfer_count = 0
        for relative_path in targets:
            entry = self.catalog.get(relative_path)
            if not entry:
                self._print(f"Warning: {relative_path} missing from catalog, skipping")
                continue

            download_url = self._select_download_url(entry)
            normalized_url = download_url or ""
            has_scummvm_download = normalized_url.startswith("https://downloads.scummvm.org/frs/")
            filename = normalized_url.rsplit("/", 1)[-1] if normalized_url else relative_path

            exists_on_remote = self.folder_exists_on_remote(relative_path, remote_folders_remaining)
            should_process_metadata = False
            if exists_on_remote:
                self._print(f"\033[92mGame {relative_path} already exists on remote server, skipping\033[0m")
                should_process_metadata = True
            else:
                if not has_scummvm_download:
                    raise FileNotFoundError(f"Game {relative_path} missing on remote and lacks ScummVM download URL")

                local_folder_path = self.download_dir / relative_path
                local_zip_path = self.download_dir / filename if filename.endswith(".zip") else None
                allow_transfers = max_transfers is None or transfer_count < max_transfers

                if filename.endswith(".zip") and local_folder_path.exists():
                    upload_succeeded = False
                    if allow_transfers and self.upload_folder(local_folder_path):
                        transfer_count += 1
                        upload_succeeded = True
                    should_process_metadata = True
                    if local_folder_path.exists():
                        if local_folder_path.is_dir():
                            shutil.rmtree(local_folder_path)
                        else:
                            local_folder_path.unlink()
                    if upload_succeeded:
                        remote_folders_for_validation.add(relative_path)
                else:
                    file_path = self.download_dir / filename
                    temp_file_path = self.download_dir / f"{filename}.downloading"
                    if temp_file_path.exists():
                        temp_file_path.unlink()
                        self._print(f"Cleaned up stale temp download: {temp_file_path}")

                    if allow_transfers:
                        if not file_path.exists():
                            downloaded_file = self.download_file(normalized_url, filename)
                        else:
                            downloaded_file = file_path

                        if filename.endswith(".zip"):
                            extracted_folder = self.extract_zip(downloaded_file)
                            if self.upload_folder(extracted_folder):
                                transfer_count += 1
                                remote_folders_for_validation.add(relative_path)
                        should_process_metadata = True
                    else:
                        if file_path.exists():
                            file_path.unlink()
                        if local_folder_path.exists():
                            if local_folder_path.is_dir():
                                shutil.rmtree(local_folder_path)
                            else:
                                local_folder_path.unlink()
                        if local_zip_path and local_zip_path.exists():
                            local_zip_path.unlink()

            if should_process_metadata:
                merged_entry = self.merged_metadata_by_path.get(relative_path)
                if merged_entry:
                    self.processed_games_metadata.append(merged_entry)
                else:
                    self._print(f"Warning: No metadata found for {relative_path}")

        if not requested_ids and self.scp_server and self.scp_path:
            errors, warnings = validate_remote_folders(remote_folders_for_validation, self.catalog)
            if errors:
                self._print("\033[91mError: Orphaned folders on remote server:\033[0m")
                for message in errors:
                    self._print(f"  - {message}")
                raise RuntimeError("Remote server contains folders not present in sheets/metadata")
            if warnings:
                self._print("\033[91mError: Required folders missing on remote server:\033[0m")
                for warning in warnings:
                    self._print(f"  - {warning}")
                raise RuntimeError("Remote server is missing folders that should have been synced")

        if self.processed_games_metadata:
            self.generate_processed_games_json()
        else:
            self._print("No games were processed, skipping games.json generation")

        self._print("Building HTTP index after all uploads...")
        self.build_http_index()


def main():
    parser = argparse.ArgumentParser(
        description='Download ScummVM games and demos',
        epilog='''
Environment Variables:
  SSH_KEY_PATH    Path to SSH private key for SCP authentication
                  (e.g., ~/.ssh/id_rsa)
  SSH_PASSWORD    SSH password for authentication (requires sshpass)
                  Note: SSH keys are preferred over passwords for security
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('games', nargs='*', help='Game IDs to download (if none specified, downloads all)')
    parser.add_argument('--download-dir', default='games', help='Directory to download games to')
    parser.add_argument('--scp-server', help='SCP server for uploading (user@host)')
    parser.add_argument('--scp-path', help='Remote path for uploading games')
    parser.add_argument('--scp-port', type=int, help='SSH/SCP port (default: 22)')
    parser.add_argument('--max-transfers', type=int, help='Maximum number of games to transfer (excluding skipped ones)')
    
    args = parser.parse_args()
    
    # Filter out testbed and playground3d
    game_ids = [g for g in args.games if g not in ['testbed', 'playground3d']]
    
    # Fallback to environment variables if CLI args are not provided
    scp_server = args.scp_server or (os.environ.get('SSH_USER') + '@' + os.environ.get('SSH_HOST') if os.environ.get('SSH_USER') and os.environ.get('SSH_HOST') else None)
    scp_path = args.scp_path or os.environ.get('SSH_PATH')
    scp_port = args.scp_port or (int(os.environ.get('SSH_PORT')) if os.environ.get('SSH_PORT') else None)
    downloader = GameDownloader(download_dir=args.download_dir, scp_server=scp_server, scp_path=scp_path, scp_port=scp_port)

    connection_opened = False
    if scp_server and scp_path:
        downloader.open_connection()
        connection_opened = True

    try:
        metadata_path = Path(__file__).parent.parent / "assets" / "metadata.json"
        downloader.refresh_catalog(metadata_path)
        downloader.download_and_process_games(game_ids, args.max_transfers)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    finally:
        if connection_opened:
            try:
                downloader.close_connection()
            except RuntimeError:
                pass


if __name__ == "__main__":
    main()