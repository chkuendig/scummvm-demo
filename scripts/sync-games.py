#!/usr/bin/env python3
"""
ScummVM Game Downloader and Uploader
Rewritten from JavaScript using only standard library
"""

import os
import sys
import urllib.request
import urllib.parse
import zipfile
import shutil
import subprocess
import argparse
import json
from pathlib import Path
import tempfile

# Constants
SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQamumX0p-DYQa5Umi3RxX-pHM6RZhAj1qvUP0jTmaqutN9FwzyriRSXlO9rq6kR60pGIuPvCDzZL3s/pub?output=tsv'
SHEET_IDS = {
    'platforms': '1061029686',
    'compatibility': '1989596967', 
    'games': '1775285192',
    'engines': '0',
    'companies': '226191984',
    'versions': '1225902887',
    'game_demos': '1303420306',
    'series': '1095671818',
    'screenshots': '168506355',
    'scummvm_downloads': '1057392663',
    'game_downloads': '810295288',
    'director_demos': '1256563740',
}

class GameDownloader:
    def __init__(self, download_dir="games", scp_server=None, scp_path=None):
        self.games = {}
        self.all_download_urls = []  # List to store all URLs we want to download
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.scp_server = scp_server
        self.scp_path = scp_path
        self.compatible_game_ids = set()  # Cache for compatible game IDs
    
    def _temp_print(self, message, file=sys.stderr):
        """Print a temporary message that will be overwritten, padded to terminal width"""
        try:
            # Get terminal width, default to 80 if not available
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80
        
        # Pad the message with spaces to clear any previous text
        padded_message = message.ljust(terminal_width)
        print(padded_message, end='\r', flush=True, file=file)
    
    def _print(self, message, file=sys.stderr):
        """Print a permanent message, padded to terminal width"""
        try:
            # Get terminal width, default to 80 if not available
            terminal_width = os.get_terminal_size().columns
        except OSError:
            terminal_width = 80
        
        # Pad the message with spaces to clear any previous text
        padded_message = message.ljust(terminal_width)
        print(padded_message, file=file)
    
    def _build_ssh_command(self, base_command='ssh'):
        """Build SSH/SCP command with authentication options
        Returns (command_list, environment_dict)"""
        cmd = []
        env = os.environ.copy()
        
        # Check for password authentication first
        ssh_password = os.environ.get('SSH_PASSWORD')
        if ssh_password:
            cmd.extend(['sshpass', '-e', base_command])
            env['SSHPASS'] = ssh_password
        else:
            cmd.append(base_command)
        
        # Add SSH key if specified in environment (and no password)
        ssh_key = os.environ.get('SSH_KEY_PATH')
        if ssh_key and not ssh_password:
            cmd.extend(['-i', ssh_key])
        
        # Add other SSH options for non-interactive mode
        if ssh_password:
            cmd.extend(['-o', 'StrictHostKeyChecking=no'])
        else:
            cmd.extend([
                '-o', 'BatchMode=yes',
                '-o', 'StrictHostKeyChecking=no'
            ])
        
        return cmd, env
        
    def get_google_sheet(self, url):
        """Fetch Google Sheet with redirect handling"""
        try:
            # Handle redirects manually
            req = urllib.request.Request(url)
            response = urllib.request.urlopen(req)
            
            # Check if we got a redirect
            if response.getcode() in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    response = urllib.request.urlopen(redirect_url)
            
            return response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            raise
    
    def parse_tsv(self, text):
        """Parse TSV data into list of dictionaries"""
        lines = text.split('\r\n')
        if not lines:
            return []
        
        headers = lines[0].split('\t')
        result = []
        
        for i in range(1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            values = line.split('\t')
            row = {}
            for col, value in enumerate(values):
                if col < len(headers):
                    row[headers[col]] = value
            result.append(row)
        
        return result
    
    def get_compatible_games(self):
        """Fetch compatible game IDs from Google Sheets"""
        self._temp_print("Fetching list of compatible games")
        url = f"{SHEET_URL}&gid={SHEET_IDS['compatibility']}"
        body = self.get_google_sheet(url)
        
        games_data = self.parse_tsv(body)
        for game in games_data:
            # Try multiple possible column names for game ID
            game_id = game.get('id', '') or game.get('game_id', '') or game.get('gameid', '')
            if game_id:
                self.compatible_game_ids.add(game_id)
        
        self._print(f"Found {len(self.compatible_game_ids)} compatible games")
    
    def get_game_downloads(self):
        """Fetch game downloads from Google Sheets"""
        self._temp_print("Fetching list of game downloads")
        url = f"{SHEET_URL}&gid={SHEET_IDS['game_downloads']}"
        body = self.get_google_sheet(url)
        
        unique_urls = set()
        skipped_games_count = 0
        skipped_addons_count = 0
        for download in self.parse_tsv(body):
            game_id = download.get('game_id', '')
            game_name = download.get('name', '')
            category = download.get('category', '')
            
            # Skip entries with "addon" in the name (case-insensitive)
            if 'addon' in game_name.lower() or 'manuals' in game_name.lower() or category != 'games':
                skipped_addons_count += 1
                continue
                        
            # Allow specifying game names without target/engine name
            short_name = game_id[game_id.rfind(':') + 1:] if ':' in game_id else game_id
            
            # Skip games not found in compatibility sheet
            if game_id not in self.compatible_game_ids:
                skipped_games_count += 1
                continue
            
            # Track unique URLs for compatible games
            download_url = f"/frs/extras/{download['url']}"
            unique_urls.add(download_url)
            
            # Add to list of all URLs to download
            self.all_download_urls.append(download_url)
            
            # Always add to games dictionary (allow multiple URLs per game_id)
            self.games[game_id] = download_url
            self.games[short_name] = download_url
            
            # Add filename variants
            filename = download['url'][download['url'].rfind('/'):]
            self.games[f"{game_id}{filename}"] = download_url
            self.games[f"{short_name}{filename}"] = download_url
        
        summary_parts = [f"Found {len(unique_urls)} compatible game downloads"]
        if skipped_games_count > 0:
            summary_parts.append(f"{skipped_games_count} skipped as incompatible")
        if skipped_addons_count > 0:
            summary_parts.append(f"{skipped_addons_count} addons skipped")
  
        
        summary = f"{summary_parts[0]} ({', '.join(summary_parts[1:])})" if len(summary_parts) > 1 else summary_parts[0]
        self._print(summary)
    
    def get_demos(self):
        """Fetch game demos from Google Sheets"""
        self._temp_print("Fetching list of game demos")
        url = f"{SHEET_URL}&gid={SHEET_IDS['game_demos']}"
        body = self.get_google_sheet(url)
        
        unique_urls = set()
        skipped_demos_count = 0
        for download in self.parse_tsv(body):
            game_id = download.get('id', '')
            
            # Allow specifying game names without target/engine name
            short_name = game_id[game_id.rfind(':') + 1:] if ':' in game_id else game_id
            
            # Skip games not found in compatibility sheet
            if game_id not in self.compatible_game_ids:
                skipped_demos_count += 1
                continue
            
            # Track unique URLs for compatible games
            demo_url = download['url']
            unique_urls.add(demo_url)
            
            # Add to list of all URLs to download
            self.all_download_urls.append(demo_url)
            
            # Always add to games dictionary (allow multiple URLs per game_id)
            self.games[game_id] = demo_url
            self.games[short_name] = demo_url
            
            filename = download['url'][download['url'].rfind('/'):]
            self.games[f"{game_id}{filename}"] = demo_url
            self.games[f"{short_name}{filename}"] = demo_url
        
        self._print(f"Found {len(unique_urls)} compatible demos ({skipped_demos_count} skipped as incompatible)")
    
    def get_director_demos(self):
        """Fetch director demos from Google Sheets"""
        self._temp_print("Fetching list of director demos")
        url = f"{SHEET_URL}&gid={SHEET_IDS['director_demos']}"
        body = self.get_google_sheet(url)
        
        if not body:
            raise Exception('Failed to fetch director demos')
        
        unique_urls = set()
        skipped_director_demos_count = 0
        for download in self.parse_tsv(body):
            game_id = download.get('id', '')
            
            # Allow specifying game names without target/engine name
            short_name = game_id[game_id.rfind(':') + 1:] if ':' in game_id else game_id
            
            # Skip games not found in compatibility sheet
            if game_id not in self.compatible_game_ids:
                skipped_director_demos_count += 1
                continue
            
            # Track unique URLs for compatible games
            director_demo_url = download['url']
            unique_urls.add(director_demo_url)
            
            # Add to list of all URLs to download
            self.all_download_urls.append(director_demo_url)
            
            # Always add to games dictionary (allow multiple URLs per game_id)
            self.games[game_id] = director_demo_url
            self.games[short_name] = director_demo_url
            
            filename = download['url'][download['url'].rfind('/'):]
            self.games[f"{game_id}{filename}"] = director_demo_url
            self.games[f"{short_name}{filename}"] = director_demo_url
        
        self._print(f"Found {len(unique_urls)} compatible director demos ({skipped_director_demos_count} skipped as incompatible)")
    
    def download_file(self, url, filename):
        """Download a file from URL with atomic operation"""
        filepath = self.download_dir / filename
        temp_filepath = self.download_dir / f"{filename}.downloading"
        
        try:
            # URL encode the path to handle spaces and special characters
            parsed_url = urllib.parse.urlparse(url)
            encoded_path = urllib.parse.quote(parsed_url.path, safe='/')
            encoded_url = urllib.parse.urlunparse((
                parsed_url.scheme, parsed_url.netloc, encoded_path,
                parsed_url.params, parsed_url.query, parsed_url.fragment
            ))
            
            self._temp_print(f"Downloading {encoded_url}")
            
            # Download to temporary file first
            urllib.request.urlretrieve(encoded_url, temp_filepath)
            
            # Only move to final location if download completed successfully
            temp_filepath.rename(filepath)
            self._temp_print(f"Download completed: {filename}")

            return filepath
        except Exception as e:
            # Clean up temp file if download failed
            if temp_filepath.exists():
                temp_filepath.unlink()
                self._print(f"Cleaned up incomplete download: {temp_filepath}")
            self._print(f"Error downloading {url}: {e}")
            raise
    
    def extract_zip(self, zip_path):
        """Extract zip file and return the extracted folder path"""
        zip_path = Path(zip_path)
        extract_dir = self.download_dir / zip_path.stem
        
        if extract_dir.exists():
            self._print(f"Directory {extract_dir} already exists, skipping extraction")
            return extract_dir
        
        self._temp_print(f"Extracting {zip_path} to {extract_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Remove the zip file after extraction
        zip_path.unlink()
        self._temp_print(f"Removed {zip_path}")
        
        return extract_dir
    
    def folder_exists_on_remote(self, folder_name):
        """Check if folder exists on remote server"""
        if not self.scp_server or not self.scp_path:
            return False
        
        try:
            ssh_cmd, env = self._build_ssh_command()
            ssh_cmd.extend([
                self.scp_server,
                f'test -d "{self.scp_path}/{folder_name}"'
            ])
            
            result = subprocess.run(ssh_cmd, capture_output=True, check=False, env=env)
            return result.returncode == 0
        except Exception as e:
            self._print(f"Error checking remote folder: {e}")
            return False
    
    def upload_folder(self, folder_path):
        """Upload folder to remote server via SCP with atomic upload handling
        Returns True if upload occurred, False if skipped"""
        if not self.scp_server or not self.scp_path:
            self._print("No SCP server configured, skipping upload")
            return False
        
        folder_path = Path(folder_path)
        folder_name = folder_path.name
        
        # Upload to temporary location first for atomic operation
        temp_name = f"{folder_name}.uploading"
        
        # Clean up any existing temp folder first
        try:
            cleanup_cmd, env = self._build_ssh_command()
            cleanup_cmd.extend([
                self.scp_server,
                f'rm -rf "{self.scp_path}/{temp_name}"'
            ])
            
            subprocess.run(cleanup_cmd, check=False, env=env, capture_output=True)
            self._temp_print(f"Cleaned up any existing temp folder {temp_name}")
        except Exception:
            pass  # Ignore cleanup errors
        
        try:
            self._temp_print(f"Uploading {folder_path} to {self.scp_server}:{self.scp_path}/{temp_name}")
            
            # Prepare SCP command - upload to temporary name
            scp_cmd, env = self._build_ssh_command('scp')
            scp_cmd.append('-r')  # Add recursive flag for SCP
            
            # Upload to temp location
            scp_cmd.extend([
                str(folder_path),
                f"{self.scp_server}:{self.scp_path}/{temp_name}"
            ])
            
            # Upload to temp location
            subprocess.run(scp_cmd, check=True, env=env)
            
            # Prepare SSH command for atomic move
            ssh_cmd, env = self._build_ssh_command()
            ssh_cmd.extend([
                self.scp_server,
                f'mv "{self.scp_path}/{temp_name}" "{self.scp_path}/{folder_name}"'
            ])
            
            # Move to final location atomically
            subprocess.run(ssh_cmd, check=True, env=env)
            
            self._print(f"\033[1;32mGame {folder_name} successfully uploaded\033[0m")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self._print(f"Upload failed for {folder_name}: {e}")
            # Clean up temp folder on remote if it exists
            try:
                cleanup_cmd, env = self._build_ssh_command()
                cleanup_cmd.extend([
                    self.scp_server,
                    f'rm -rf "{self.scp_path}/{temp_name}"'
                ])
                subprocess.run(cleanup_cmd, check=False, env=env)
                self._print(f"Cleaned up failed upload temp folder {temp_name}")
            except Exception:
                pass
            return False
    
    def build_http_index(self):
        """Run the HTTP index building script on the remote server"""
        if not self.scp_server or not self.scp_path:
            return
        
        # Embedded HTTP index building script content
        index_script = '''#!/usr/bin/env python3
import os
import json
import sys
from pathlib import Path

sym_links = {}
ignore_files = ['.git', 'index.json']

def rd_sync(dpath, tree, name):
    """Recursively scan directory and build file tree structure."""
    try:
        files = os.listdir(dpath)
    except (OSError, PermissionError):
        return tree
    
    for file in files:
        # ignore non-essential directories / files
        if file in ignore_files or file.startswith('.'):
            continue
            
        fpath = os.path.join(dpath, file)
        
        try:
            # Avoid infinite loops with symbolic links
            lstat = os.lstat(fpath)
            if os.path.islink(fpath):
                dev = lstat.st_dev
                ino = lstat.st_ino
                
                if dev not in sym_links:
                    sym_links[dev] = {}
                
                # Ignore if we've seen it before
                if ino in sym_links[dev]:
                    continue
                    
                sym_links[dev][ino] = True
            
            if os.path.isdir(fpath):
                child = {}
                tree[file] = child
                rd_sync(fpath, child, file)
                
                # Write index.json for this directory
                fs_listing = json.dumps(child)
                fname = os.path.join(fpath, "index.json")
                with open(fname, 'w', encoding='utf-8') as f:
                    f.write(fs_listing)
                
                # Reset tree entry to empty dict after writing index
                tree[file] = {}
            else:
                # Store file size
                stat = os.stat(fpath)
                tree[file] = stat.st_size
                
        except (OSError, PermissionError):
            # Ignore and move on
            continue
    
    return tree

def main():
    if len(sys.argv) == 2:
        root_folder = sys.argv[1]
        fs_listing = json.dumps(rd_sync(root_folder, {}, '/'))
        fname = os.path.join(root_folder, "index.json")
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(fs_listing)
    else:
        root_folder = os.getcwd()
        fs_listing = json.dumps(rd_sync(root_folder, {}, '/'))
        print(fs_listing)

if __name__ == "__main__":
    main()
'''
        
        try:
            # Create a command that writes the script and executes it
            remote_command = f'''cat > /tmp/build_http_index.py << 'EOF'
{index_script}
EOF
python3 /tmp/build_http_index.py "{self.scp_path}" && rm /tmp/build_http_index.py'''
            
            ssh_cmd, env = self._build_ssh_command()
            ssh_cmd.extend([self.scp_server, remote_command])
            
            self._temp_print("Building HTTP index on remote server...")
            result = subprocess.run(ssh_cmd, capture_output=True, check=False, env=env)
            
            if result.returncode == 0:
                self._temp_print("HTTP index built successfully")
            else:
                self._print(f"Warning: HTTP index build failed: {result.stderr.decode('utf-8', errors='ignore')}")
                
        except Exception as e:
            self._print(f"Error building HTTP index: {e}")

    def _get_target_name_for_game_id(self, game_id):
        """Get the target filename/foldername that would be created for a game_id"""
        if game_id.startswith('http'):
            url = game_id
            filename = url[url.rfind('/') + 1:]
        elif game_id not in self.games:
            return game_id  # Fallback to game_id if not found
        else:
            url = f"https://downloads.scummvm.org{self.games[game_id]}"
            temp_game_id = game_id
            if '/' in temp_game_id:
                temp_game_id = temp_game_id[:temp_game_id.rfind('/')]
            temp_game_id = temp_game_id[temp_game_id.rfind(':') + 1:]  # Remove target from target:gameId
            filename = url[url.rfind('/') + 1:]
            if not filename.startswith(temp_game_id):
                filename = f"{temp_game_id}-{filename}"
        
        # Return the target name (folder name after extraction or file name)
        if filename.endswith('.zip'):
            return filename[:-4]  # Remove .zip extension
        else:
            return filename
    
    def download_and_process_games(self, game_ids, max_transfers=None):
        """Download, extract, and optionally upload games"""
        transfer_count = 0
        any_uploads_occurred = False
        
        for game_id in game_ids:
            # Check if we've reached the transfer limit
            if max_transfers is not None and transfer_count >= max_transfers:
                self._print(f"Reached transfer limit of {max_transfers}, stopping")
                break
            try:
                if game_id.startswith('http'):
                    url = game_id
                    filename = url[url.rfind('/') + 1:]
                elif game_id not in self.games:
                    self._print(f"GameID {game_id} not known")
                    sys.exit(1)
                else:
                    url = f"https://downloads.scummvm.org{self.games[game_id]}"
                    if '/' in game_id:
                        game_id = game_id[:game_id.rfind('/')]
                    game_id = game_id[game_id.rfind(':') + 1:]  # Remove target from target:gameId
                    filename = url[url.rfind('/') + 1:]
                    if not filename.startswith(game_id):
                        filename = f"{game_id}-{filename}"
                                
                # Determine the final folder/file name that would exist on remote
                if filename.endswith('.zip'):
                    target_name = filename[:-4]  # Remove .zip extension
                    local_folder_path = self.download_dir / target_name
                    local_zip_path = self.download_dir / filename
                else:
                    target_name = filename
                    local_folder_path = self.download_dir / filename
                    local_zip_path = None
                
                # Check if already exists on remote server (do this check once)
                exists_on_remote = self.folder_exists_on_remote(target_name)
                if exists_on_remote:
                    self._print(f"\033[92mGame {target_name} already exists on remote server, skipping\033[0m")
                    # Clean up any local files for completed remote games
                    if local_folder_path.exists():
                        if local_folder_path.is_dir():
                            shutil.rmtree(local_folder_path)
                        else:
                            local_folder_path.unlink()
                        self._temp_print(f"Cleaned up local file/folder {local_folder_path.name} (already on remote)")
                    if local_zip_path and local_zip_path.exists():
                        local_zip_path.unlink()
                        self._temp_print(f"Cleaned up local zip file {local_zip_path.name} (already on remote)")
                    continue
                
                # Check if extracted folder already exists locally
                if filename.endswith('.zip') and local_folder_path.exists():
                    self._temp_print(f"Folder {local_folder_path} already exists, skipping download")
                    # Upload since we know it doesn't exist on remote
                    if self.upload_folder(local_folder_path):
                        transfer_count += 1
                        any_uploads_occurred = True
                    continue
                
                # Check if file already exists locally
                file_path = self.download_dir / filename
                temp_file_path = self.download_dir / f"{filename}.downloading"
                
                # Clean up any stale temp download files
                if temp_file_path.exists():
                    temp_file_path.unlink()
                    self._print(f"Cleaned up stale temp download: {temp_file_path}")
                
                if not file_path.exists():
                    downloaded_file = self.download_file(url, filename)
                else:
                    downloaded_file = file_path
                    self._temp_print(f"File {filename} already exists, skipping download")

                # Extract if it's a zip file
                if filename.endswith('.zip'):
                    extracted_folder = self.extract_zip(downloaded_file)
                    # Upload the extracted folder
                    if self.upload_folder(extracted_folder):
                        transfer_count += 1
                        any_uploads_occurred = True
              
                    
            except Exception as e:
                self._print(f"Error processing {game_id}: {e}")
                continue
        
        # Build HTTP index once after all uploads are complete
        if any_uploads_occurred and self.scp_server and self.scp_path:
            self._print("Building HTTP index after all uploads...")
            self.build_http_index()
    
    def run(self, game_ids=None, max_transfers=None):
        """Main execution function"""
        # Fetch compatibility data first
        self.get_compatible_games()
        
        # Fetch all game lists
        self.get_game_downloads()
        self.get_demos()
        self.get_director_demos()
        
        # If no game IDs specified, download all games
        if not game_ids:
            # Use all collected URLs, but convert them to a format that download_and_process_games expects
            # Get unique URLs to avoid downloading the same file multiple times
            unique_urls = list(set(self.all_download_urls))
            # Convert URLs to full HTTP URLs for processing
            game_ids = []
            for url in unique_urls:
                if url.startswith('/frs/'):
                    full_url = f"https://downloads.scummvm.org{url}"
                else:
                    full_url = url
                game_ids.append(full_url)
        
        # Sort game_ids by their target filename/foldername for consistent processing order (case-insensitive)
        game_ids.sort(key=lambda x: self._get_target_name_for_game_id(x).lower())
        
        self.download_and_process_games(game_ids, max_transfers)

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
    parser.add_argument('--max-transfers', type=int, help='Maximum number of games to transfer (excluding skipped ones)')
    
    args = parser.parse_args()
    
    # Filter out testbed and playground3d
    game_ids = [g for g in args.games if g not in ['testbed', 'playground3d']]
    
    downloader = GameDownloader(
        download_dir=args.download_dir,
        scp_server=args.scp_server,
        scp_path=args.scp_path
    )
    
    try:
        downloader.run(game_ids if game_ids else None, args.max_transfers)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()