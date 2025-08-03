#!/usr/bin/env python3
"""Generate a minimal games.json based on remote content and metadata."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set

from helper_gsheet import (
    build_unified_demo_catalog,
    validate_remote_folders,
    create_json_entry,
)
from helper_ssh import SSHHelper
def list_remote_folders(ssh_helper: SSHHelper, server: str, base_path: str) -> Set[str]:
    """Return the set of direct subdirectories on the remote server."""
    if not server or not base_path:
        raise ValueError("Both server and base_path are required to list remote folders")

    base_cmd = ssh_helper.build_controlpath_command()
    env = os.environ.copy()
    base_cmd.extend([server, f'ls -1 "{base_path}"'])

    result = subprocess.run(base_cmd, capture_output=True, text=True, env=env, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"Failed to list remote folders (exit {result.returncode}): {stderr}")

    folders: Set[str] = set()
    for line in result.stdout.splitlines():
        entry = line.strip()
        if not entry:
            continue
        test_cmd = ssh_helper.build_controlpath_command()
        test_cmd.extend([server, f'test -d "{base_path}/{entry}"'])
        test_result = subprocess.run(test_cmd, capture_output=True, env=env, check=False)
        if test_result.returncode == 0:
            folders.add(entry)
    return folders


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate games.json from remote demos and metadata")
    parser.add_argument("--output", default="games.json", help="Path to write the generated games.json")
    parser.add_argument("--metadata", default=str(Path(__file__).parent.parent / "assets" / "metadata.json"), help="Path to metadata.json")
    parser.add_argument("--scp-server", help="SCP/SSH server in user@host format")
    parser.add_argument("--scp-path", help="Remote path containing demo folders")
    parser.add_argument("--scp-port", type=int, help="SSH/SCP port (default 22)")
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    
    # Build unified demo catalog with all the logic centralized
    demo_catalog = build_unified_demo_catalog(metadata_path)

    # Get remote server connection details
    scp_server = args.scp_server or (
        f"{os.environ['SSH_USER']}@{os.environ['SSH_HOST']}" if os.environ.get("SSH_USER") and os.environ.get("SSH_HOST") else None
    )
    scp_path = args.scp_path or os.environ.get("SSH_PATH")
    scp_port = args.scp_port or (int(os.environ["SSH_PORT"]) if os.environ.get("SSH_PORT") else None)

    if not scp_server or not scp_path:
        print("Error: scp-server and scp-path must be provided via arguments or environment", file=sys.stderr)
        return 1

    # List remote folders
    ssh_helper = SSHHelper(scp_server, scp_port)
    ssh_helper.open_persistent_connection()
    try:
        remote_folders = list_remote_folders(ssh_helper, scp_server, scp_path)
    finally:
        ssh_helper.close_persistent_connection()

    # Validate using improved logic
    errors, warnings = validate_remote_folders(remote_folders, demo_catalog)
    
    has_errors = False
    if errors:
        print("\033[91mError: Orphaned folders on remote server:\033[0m", file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
        has_errors = True
    if warnings:
        print("\033[91mError: Required folders missing on remote server:\033[0m", file=sys.stderr)
        for warning in warnings:
            print(f"  - {warning}", file=sys.stderr)
        has_errors = True

    # Build final entries list - only include folders that exist on server and should be included
    entries: List[Dict[str, object]] = []
    for folder in sorted(remote_folders):
        entry_data = demo_catalog.get(folder)
        if entry_data is None:
            print(f"\033[91mValidation error: {folder} missing in demo catalog\033[0m", file=sys.stderr)
            has_errors = True
            continue
        if not entry_data.should_include_in_json:
            print(f"\033[91mValidation error: {folder} should not be included in JSON \033[0m", file=sys.stderr)
            has_errors = True
            continue
        
        # Create JSON entry using the new method
        json_entry = create_json_entry(entry_data)
        entries.append(json_entry)

    entries.sort(key=lambda item: (str(item.get("id", "")).lower(), item["relative_path"].lower()))

    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(entries, handle, indent=2, ensure_ascii=False)

    print(f"Wrote {len(entries)} entries to {output_path}")
    
    # Return 1 if there were validation errors, 0 otherwise
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
