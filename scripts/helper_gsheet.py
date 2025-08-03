"""Shared helpers for building the demo/game catalog from sheets, metadata and remote state."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple

import json
import sys
import urllib.parse
import urllib.request

# Google Sheets utilities
_REDIRECT_CODES = {301, 302, 303, 307, 308}


def fetch_sheet(url: str, *, timeout: Optional[float] = None) -> str:
    """Return the sheet contents as text, following a single redirect if needed."""
    request = urllib.request.Request(url)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.getcode() in _REDIRECT_CODES:
            redirect_url = response.headers.get("Location")
            if redirect_url:
                with urllib.request.urlopen(redirect_url, timeout=timeout) as redirected:
                    return redirected.read().decode("utf-8")
        return response.read().decode("utf-8")


def parse_tsv(body: str) -> list[dict[str, str]]:
    """Parse TSV text into a list of row dictionaries keyed by header."""
    if not body:
        return []

    lines = body.split("\r\n")
    if not lines:
        return []

    headers = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        values = line.split("\t")
        row = {headers[i]: value for i, value in enumerate(values) if i < len(headers)}
        rows.append(row)
    return rows


# Game catalog constants and configuration
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQamumX0p-DYQa5Umi3RxX-pHM6RZhAj1qvUP0jTmaqutN9FwzyriRSXlO9rq6kR60pGIuPvCDzZL3s/pub?output=tsv"
SHEET_IDS = {
    "compatibility": "1989596967",
    "game_demos": "1303420306",
    "game_downloads": "810295288",
    "director_demos": "1256563740",
    "platforms": "1061029686",
}

ALLOWED_FIELDS = {"id", "relative_path", "description", "download_url", "languages", "platform"}
LANGUAGE_COLUMNS = ["lang", "language", "language1", "language2", "language3"]
_SOURCE_PRIORITY = {"game_demos": 3, "director_demos": 2, "game_downloads": 1}


def normalize_download_url(url: str) -> str:
    value = (url or "").strip()
    if not value:
        return value
    if value.startswith("/frs/"):
        return f"https://downloads.scummvm.org{value}"
    if value.startswith("frs/"):
        return f"https://downloads.scummvm.org/{value}"
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("downloads.scummvm.org"):
        return f"https://{value}"
    return value


@dataclass
class CombinedEntry:
    """Represents merged information for a single demo/game folder."""

    relative_path: str
    metadata: Optional[Dict[str, object]]
    demo_row: Optional[Dict[str, str]]
    game_id: Optional[str]
    sheet_download_url: Optional[str]
    sheet_download_url_relative: Optional[str]
    source: Optional[str]
    
    # Additional computed flags for better decision making
    is_in_compatibility_table: bool = False
    is_skip_forced: Optional[bool] = None  # True=skip, False=force include, None=use default logic
    should_sync: bool = False
    should_include_in_json: bool = False


def _game_id_from_row(row: Dict[str, str]) -> Optional[str]:
    return (row.get("id") or row.get("game_id") or row.get("gameid") or "").strip() or None


def compute_relative_path(url: str) -> str:
    if not url:
        return ""
    filename = url.rsplit("/", maxsplit=1)[-1]
    return filename[:-4] if filename.endswith(".zip") else ""

def extract_languages(row: Dict[str, str]) -> Optional[List[str]]:
    languages: List[str] = []
    for column in LANGUAGE_COLUMNS:
        value = (row.get(column) or "").strip()
        if value and value not in languages:
            languages.append(value)
    return languages or None


def load_metadata(metadata_path: Path) -> Dict[str, Dict[str, object]]:
    if not metadata_path.exists():
        return {}

    with open(metadata_path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)

    if not isinstance(raw, dict):
        raise ValueError("metadata.json must contain an object at the top level")

    metadata_by_path: Dict[str, Dict[str, object]] = {}

    for relative_path, entry in raw.items():
        if not isinstance(entry, dict):
            entry = {}
        entry_copy = entry.copy()
        entry_copy.setdefault("relative_path", relative_path)
        metadata_by_path[relative_path] = entry_copy

    return metadata_by_path


def fetch_sheet_rows(sheet_id: str) -> List[Dict[str, str]]:
    url = f"{SHEET_URL}&gid={sheet_id}"
    body = fetch_sheet(url, timeout=30)  # 30 second timeout
    return parse_tsv(body)


def fetch_compatibility_ids() -> Set[str]:
    rows = fetch_sheet_rows(SHEET_IDS["compatibility"])
    result: Set[str] = set()
    for row in rows:
        game_id = _game_id_from_row(row)
        if game_id:
            result.add(game_id)
    return result


def add_rows_to_demo_map(
    demo_map: Dict[str, Dict[str, object]],
    rows: Iterable[Dict[str, str]],
    source: str,
    *,
    platform_lookup: Optional[Dict[str, str]] = None,
    compatibility_ids: Optional[Set[str]] = None,
    metadata_by_path: Optional[Dict[str, Dict[str, object]]] = None,
) -> Tuple[int, int, int, int]:
    """
    Add rows from a sheet to the demo map.
    
    Returns (added_count, skipped_count, kept_manually_count, skipped_manually_count) tuple with statistics.
    """
    priority = _SOURCE_PRIORITY.get(source, 0)
    added_count = 0
    skipped_count = 0
    kept_manually_count = 0
    skipped_manually_count = 0
    
    for row in rows:
        url_value = (row.get("url") or "").strip()
        if not url_value:
            continue

        if source == "game_downloads":
            name_value = (row.get("name") or "").strip().lower()
            category_value = (row.get("category") or "").strip().lower()
            if "addon" in name_value or "manuals" in name_value:
                skipped_count += 1
                continue
            if category_value and category_value != "games":
                skipped_count += 1
                continue

            extras_path = url_value.lstrip("/")
            if not extras_path:
                continue
            relative_url = f"/frs/extras/{extras_path}"
            absolute_url = normalize_download_url(relative_url)
        else:
            if url_value.startswith(("http://", "https://")):
                parsed = urllib.parse.urlparse(url_value)
                relative_url = parsed.path or url_value
                absolute_url = normalize_download_url(url_value)
            else:
                relative_url = url_value
                absolute_url = normalize_download_url(relative_url)

        relative_path = compute_relative_path(absolute_url)
        if not relative_path:
            continue
        
        # Check compatibility table and metadata overrides
        game_id = _game_id_from_row(row)
        metadata_entry = metadata_by_path.get(relative_path) if metadata_by_path else None
        skip_flag = metadata_entry.get("skip") if metadata_entry else None
        
        if compatibility_ids is not None and game_id:
            is_compatible = game_id in compatibility_ids
            
            if is_compatible:
                # Compatible game - check if manually skipped
                if skip_flag is True:
                    skipped_manually_count += 1
                    continue
            else:
                # Incompatible game - check if manually kept
                if skip_flag is False:
                    kept_manually_count += 1
                    # Continue to add it despite not being compatible
                else:
                    skipped_count += 1
                    continue

        existing = demo_map.get(relative_path)
        existing_priority = existing.get("_priority", -1) if existing else -1
        if existing and existing_priority >= priority:
            continue

        row_copy: Dict[str, object] = dict(row)
        row_copy["_source"] = source
        row_copy["_priority"] = priority
        row_copy["_game_id"] = game_id
        row_copy["_download_url"] = absolute_url
        row_copy["_download_url_relative"] = relative_url

        platform_id = (row.get("platform") or "").strip()
        if platform_lookup and platform_id:
            row_copy["_platform_name"] = platform_lookup.get(platform_id, platform_id)
        elif platform_id:
            row_copy["_platform_name"] = platform_id

        demo_map[relative_path] = row_copy
        added_count += 1
    
    return (added_count, skipped_count, kept_manually_count, skipped_manually_count)


def build_unified_demo_catalog(
    metadata_path: Path,
    compatibility_ids: Optional[Set[str]] = None,
    platform_lookup: Optional[Dict[str, str]] = None
) -> Dict[str, CombinedEntry]:
    """
    Build a unified catalog of all demos/games from sheets and metadata.
    
    This is the central function that consolidates all logic for determining
    which demos should be synced and included in JSON output.
    
    Returns a dictionary mapping relative_path -> CombinedEntry with all the 
    computed flags for sync and inclusion decisions.
    """
    if compatibility_ids is None:
        compatibility_ids = fetch_compatibility_ids()
    if platform_lookup is None:
        platform_lookup = fetch_platform_lookup()
    
    metadata_by_path = load_metadata(metadata_path)
    
    # Build initial map from sheet data
    demo_map: Dict[str, Dict[str, object]] = {}
    
    # Add game demos
    demo_rows = fetch_sheet_rows(SHEET_IDS["game_demos"])
    demos_added, demos_skipped, demos_kept_manually, demos_skipped_manually = add_rows_to_demo_map(demo_map, demo_rows, "game_demos", platform_lookup=platform_lookup, compatibility_ids=compatibility_ids, metadata_by_path=metadata_by_path)
    parts = [f"Found {demos_added} compatible game demos"]
    if demos_skipped > 0:
        parts.append(f"{demos_skipped} skipped as incompatible")
    if demos_kept_manually > 0:
        parts.append(f"{demos_kept_manually} kept manually (skip=false)")
    if demos_skipped_manually > 0:
        parts.append(f"{demos_skipped_manually} skipped manually (skip=true)")
    print(f"{parts[0]} ({', '.join(parts[1:])})" if len(parts) > 1 else parts[0], file=sys.stderr)
    
    # Add director demos  
    director_rows = fetch_sheet_rows(SHEET_IDS["director_demos"])
    director_added, director_skipped, director_kept_manually, director_skipped_manually = add_rows_to_demo_map(demo_map, director_rows, "director_demos", platform_lookup=platform_lookup, compatibility_ids=compatibility_ids, metadata_by_path=metadata_by_path)
    parts = [f"Found {director_added} compatible director demos"]
    if director_skipped > 0:
        parts.append(f"{director_skipped} skipped as incompatible")
    if director_kept_manually > 0:
        parts.append(f"{director_kept_manually} kept manually (skip=false)")
    if director_skipped_manually > 0:
        parts.append(f"{director_skipped_manually} skipped manually (skip=true)")
    print(f"{parts[0]} ({', '.join(parts[1:])})" if len(parts) > 1 else parts[0], file=sys.stderr)
    
    # Add game downloads
    downloads_rows = fetch_sheet_rows(SHEET_IDS["game_downloads"])
    downloads_added, downloads_skipped, downloads_kept_manually, downloads_skipped_manually = add_rows_to_demo_map(demo_map, downloads_rows, "game_downloads", platform_lookup=platform_lookup, compatibility_ids=compatibility_ids, metadata_by_path=metadata_by_path)
    parts = [f"Found {downloads_added} compatible game downloads"]
    if downloads_skipped > 0:
        parts.append(f"{downloads_skipped} skipped (addons/incompatible)")
    if downloads_kept_manually > 0:
        parts.append(f"{downloads_kept_manually} kept manually (skip=false)")
    if downloads_skipped_manually > 0:
        parts.append(f"{downloads_skipped_manually} skipped manually (skip=true)")
    print(f"{parts[0]} ({', '.join(parts[1:])})" if len(parts) > 1 else parts[0], file=sys.stderr)
    
    # Build unified entries with enhanced logic
    return build_combined_entries(demo_map, metadata_by_path, compatibility_ids)


def build_combined_entries(
    demo_map: Dict[str, Dict[str, object]],
    metadata_by_path: Dict[str, Dict[str, object]],
    compatibility_ids: Set[str],
) -> Dict[str, CombinedEntry]:
    combined: Dict[str, CombinedEntry] = {}

    # Process sheet entries first
    for relative_path, row in demo_map.items():
        sheet_download_url = row.get("_download_url") or ""
        sheet_download_url = str(sheet_download_url).strip() or None
        game_id = row.get("_game_id")
        
        # Get metadata (only by path lookup)
        metadata_entry = metadata_by_path.get(relative_path)
        
        # Extract skip flag from metadata
        skip_flag = None
        if metadata_entry:
            skip_value = metadata_entry.get("skip")
            if skip_value is True:
                skip_flag = True
            elif skip_value is False:
                skip_flag = False
        
        # Determine if in compatibility table
        is_in_compatibility = bool(game_id and game_id in compatibility_ids)
        
        # Determine sync logic:
        # - skip=True: never sync
        # - skip=False: always sync (force)
        # - skip=None: sync if in compatibility table OR if entry is in sheets (has demo_row)
        if skip_flag is True:
            should_sync = False
            should_include = False
        elif skip_flag is False:
            should_sync = True
            should_include = True
        else:
            # Default logic: sync if in compatibility table
            # Having sheet data alone is not enough - must be in compatibility table or metadata
            should_sync = is_in_compatibility

            if metadata_entry:
                should_include = True
            else:
                should_include = should_sync
        
        combined[relative_path] = CombinedEntry(
            relative_path=relative_path,
            metadata=metadata_entry,
            demo_row=row,  # type: ignore[arg-type]
            game_id=str(metadata_entry.get("id")) if metadata_entry and metadata_entry.get("id") else (str(game_id) if game_id else None),
            sheet_download_url=sheet_download_url,
            sheet_download_url_relative=str(row.get("_download_url_relative")) if row.get("_download_url_relative") else None,
            source=str(row.get("_source")) if row.get("_source") else None,
            is_in_compatibility_table=is_in_compatibility,
            is_skip_forced=skip_flag,
            should_sync=should_sync,
            should_include_in_json=should_include,
        )

    # Process metadata-only entries (not in sheets)
    for relative_path, metadata_entry in metadata_by_path.items():
        if relative_path in combined:
            # Already processed, just update metadata reference
            entry = combined[relative_path]
            entry.metadata = metadata_entry
            if not entry.game_id and metadata_entry.get("id"):
                entry.game_id = str(metadata_entry.get("id"))
            continue
        
        # This is a metadata-only entry
        game_id = str(metadata_entry.get("id")) if metadata_entry.get("id") else None
        
        # Extract skip flag
        skip_flag = None
        skip_value = metadata_entry.get("skip")
        if skip_value is True:
            skip_flag = True
        elif skip_value is False:
            skip_flag = False
        
        # Determine if in compatibility table
        is_in_compatibility = bool(game_id and game_id in compatibility_ids)
        
        # Determine sync logic for metadata-only entries:
        # - skip=True: never sync or include
        # - skip=False: always sync and include (force)
        # - skip=None: include in JSON but only sync if in compatibility table
        if skip_flag is True:
            should_sync = False
            should_include = False
        elif skip_flag is False:
            should_sync = True
            should_include = True
        else:
            # For metadata-only entries, always include in JSON but only sync if in compatibility table
            should_sync = is_in_compatibility
            should_include = True

        combined[relative_path] = CombinedEntry(
            relative_path=relative_path,
            metadata=metadata_entry,
            demo_row=None,
            game_id=game_id,
            sheet_download_url=None,
            source=None,
            sheet_download_url_relative=None,
            is_in_compatibility_table=is_in_compatibility,
            is_skip_forced=skip_flag,
            should_sync=should_sync,
            should_include_in_json=should_include,
        )

    return combined


def merge_entry(
    relative_path: str,
    metadata_entry: Optional[Dict[str, object]],
    demo_row: Optional[Dict[str, str]],
) -> Tuple[Dict[str, object], List[str]]:
    entry: Dict[str, object] = {"relative_path": relative_path}
    notes: List[str] = []
    skip_flag: Optional[bool] = None

    if metadata_entry is not None:
        skip_value = metadata_entry.get("skip")
        if isinstance(skip_value, bool):
            skip_flag = skip_value

    if demo_row:
        game_id = demo_row.get("_game_id") or _game_id_from_row(demo_row)
        if game_id:
            entry.setdefault("id", game_id)
        url_value = demo_row.get("_download_url")
        if url_value:
            entry.setdefault("download_url", normalize_download_url(str(url_value)))
        languages = extract_languages(demo_row)
        if languages:
            entry.setdefault("languages", languages)
        platform = (demo_row.get("_platform_name") or demo_row.get("platform") or "").strip()
        if platform:
            entry.setdefault("platform", platform)

        source = (demo_row.get("_source") or "").strip()
        if source == "game_downloads":
            name_value = (demo_row.get("name") or "").strip()
            if name_value:
                entry.setdefault("description", name_value)
        elif source == "director_demos":
            title_value = (demo_row.get("title") or "").strip()
            platform_label = platform
            description = f"{platform_label} {title_value} Demo".strip()
            if title_value and "description" not in entry:
                entry.setdefault("description", description if description else title_value)
        else:
            category = (demo_row.get("category") or "").strip()
            if category and "description" not in entry:
                platform_label = platform
                description = f"{platform_label} {category} Demo".strip()
                entry.setdefault("description", description if description else category)

    if metadata_entry:
        for key, value in metadata_entry.items():
            if key in {"skip", "relative_path"}:
                continue
            if key not in ALLOWED_FIELDS:
                continue
            if key == "download_url":
                entry[key] = normalize_download_url(str(value))
            else:
                entry[key] = value

        if "id" not in entry and metadata_entry.get("id"):
            entry["id"] = metadata_entry["id"]
        if "description" not in entry and metadata_entry.get("description"):
            entry["description"] = metadata_entry["description"]
        if "download_url" not in entry and metadata_entry.get("download_url"):
            entry["download_url"] = normalize_download_url(str(metadata_entry["download_url"]))
        if "languages" not in entry and metadata_entry.get("languages"):
            entry["languages"] = metadata_entry["languages"]
        if "platform" not in entry and metadata_entry.get("platform"):
            entry["platform"] = metadata_entry["platform"]
    
    # Only warn about missing metadata if we don't have sheet data either
    # It's fine if a file is not in the metadata file as long as it's in the gsheet
    if not metadata_entry and not demo_row:
        notes.append("Missing metadata entry")

    filtered = {key: value for key, value in entry.items() if key in ALLOWED_FIELDS and value}
    download_url = filtered.get("download_url")
    if isinstance(download_url, str):
        filtered["download_url"] = normalize_download_url(download_url)
    filtered["relative_path"] = relative_path

    if "id" not in filtered and skip_flag is not True:
        notes.append("Missing game id")

    return filtered, notes


def validate_layout(
    remote_folders: Set[str],
    combined_entries: Dict[str, CombinedEntry],
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    for folder in sorted(remote_folders):
        entry = combined_entries.get(folder)
        
        if entry is None:
            # This folder exists on server but has no mapping in either metadata or sheets
            errors.append(f"Remote folder '{folder}' has no mapping in metadata or Google Sheets")
        elif entry.is_skip_forced is True:
            # This is expected - folder marked as skip, don't report as error
            continue

    # Check for entries that should be on server but aren't
    for relative_path, entry in combined_entries.items():
        if entry.should_include_in_json and relative_path not in remote_folders:
            if entry.is_skip_forced is not True:  # Don't warn about explicitly skipped items
                errors.append(f"Entry '{relative_path}' should be on server but is missing")

    return errors, warnings


def create_json_entry(entry: CombinedEntry) -> Dict[str, object]:
    """Create a JSON entry from a CombinedEntry for games.json output."""
    result: Dict[str, object] = {"relative_path": entry.relative_path}
    
    if entry.game_id:
        result["id"] = entry.game_id
    
    # Build description from metadata or sheet data
    description = None
    if entry.metadata and entry.metadata.get("description"):
        description = str(entry.metadata["description"])
    elif entry.demo_row:
        # Build description from sheet data
        source = str(entry.demo_row.get("_source", ""))
        platform = str(entry.demo_row.get("_platform_name") or entry.demo_row.get("platform") or "").strip()
        
        if source == "game_downloads":
            name_value = str(entry.demo_row.get("name") or "").strip()
            description = name_value or None
        elif source == "director_demos":
            title_value = str(entry.demo_row.get("title") or "").strip()
            if title_value:
                description = f"{platform} {title_value} Demo".strip() if platform else title_value
        else:
            category = str(entry.demo_row.get("category") or "").strip()
            if category:
                description = f"{platform} {category} Demo".strip() if platform else category

        if not description:
            fallback_fields = ("description", "name", "title")
            for field in fallback_fields:
                raw_value = str(entry.demo_row.get(field) or "").strip()
                if raw_value:
                    description = raw_value
                    break
            if not description and platform:
                description = f"{platform} Demo"
    
    if description:
        result["description"] = description
    
    if entry.sheet_download_url:
        result["download_url"] = normalize_download_url(entry.sheet_download_url)
    elif entry.metadata and entry.metadata.get("download_url"):
        result["download_url"] = normalize_download_url(str(entry.metadata["download_url"]))
    
    # Extract languages
    languages = None
    if entry.metadata and entry.metadata.get("languages"):
        languages = entry.metadata["languages"]
        if isinstance(languages, list):
            languages = [str(lang) for lang in languages]
    elif entry.demo_row:
        languages = extract_languages(entry.demo_row)
    
    # Only include languages if there are multiple languages, or if the single language is not 'en'
    # (English-only games don't need the language specified since it's often wrong - should be en_US or en_GB)
    if languages:
        if len(languages) == 1 and languages[0].lower() == 'en':
            # Skip single 'en' language
            pass
        else:
            result["languages"] = languages
    
    # Extract platform
    platform = None
    if entry.metadata and entry.metadata.get("platform"):
        platform = str(entry.metadata["platform"])
    elif entry.demo_row:
        platform = str(entry.demo_row.get("_platform_name") or entry.demo_row.get("platform") or "").strip() or None
    
    if platform:
        result["platform"] = platform
    
    # Filter to only allowed fields and non-empty values
    filtered = {key: value for key, value in result.items() if key in ALLOWED_FIELDS and value}
    filtered["relative_path"] = entry.relative_path  # Always include this
    
    return filtered


def validate_remote_folders(
    remote_folders: Set[str],
    demo_catalog: Dict[str, CombinedEntry]
) -> Tuple[List[str], List[str]]:
    """
    Improved validation that uses the unified demo catalog.
    
    Only report errors for folders that exist on the server but have no
    mapping in either metadata or sheets.
    """
    errors: List[str] = []
    warnings: List[str] = []

    for folder in sorted(remote_folders):
        entry = demo_catalog.get(folder)
        
        if entry is None:
            # This folder exists on server but has no mapping anywhere
            errors.append(f"Remote folder '{folder}' has no mapping in metadata or Google Sheets")
        elif entry.is_skip_forced is True:
            # This is expected - folder marked as skip
            continue
        # If entry exists (in metadata or sheets), it's valid even if should_sync=False
        # The folder might be on the server from a previous sync or manual upload

    # Check for entries that should exist on server but don't
    for relative_path, entry in demo_catalog.items():
        if entry.should_sync and relative_path not in remote_folders:
            # Only warn about entries that should be synced but are missing
            # Don't warn about metadata-only entries that aren't in compatibility table
            warnings.append(f"Entry '{relative_path}' should be synced but is missing from server")

    return errors, warnings


def fetch_platform_lookup() -> Dict[str, str]:
    rows = fetch_sheet_rows(SHEET_IDS["platforms"])
    lookup: Dict[str, str] = {}
    for row in rows:
        platform_id = (row.get("id") or "").strip()
        if not platform_id:
            continue
        platform_name = (row.get("name") or "").strip() or platform_id
        lookup[platform_id] = platform_name
    return lookup