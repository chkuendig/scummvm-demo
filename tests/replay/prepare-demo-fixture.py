#!/usr/bin/env python3
"""Prepare the local Full Throttle fixture used by the browser replay test.

The ZIP is the public demo linked by ScummVM's demos page. Pin its checksum so
the replay uses the same game files every week without relying on the demo
website's Cloudflare-protected game-data CDN.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
from zipfile import ZipFile


DEMO_SHA256 = "1ba0df98349453a730dfef780f8fa9b34f284d081fd9e0e190388c73a85c88c9"
GAME_ID = "ft-dos-demo-en"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_index(path: Path, contents: dict) -> None:
    path.write_text(json.dumps(contents, sort_keys=True) + "\n", encoding="utf-8")


def write_directory_indexes(directory: Path) -> None:
    entries = {}
    for child in sorted(directory.iterdir()):
        if child.name == "index.json":
            continue
        if child.is_dir():
            write_directory_indexes(child)
            entries[child.name] = {}
        elif child.is_file():
            entries[child.name] = child.stat().st_size
    write_index(directory / "index.json", entries)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()

    actual_sha = sha256(args.archive)
    if actual_sha != DEMO_SHA256:
        raise SystemExit(f"Full Throttle demo checksum mismatch: {actual_sha}")

    games_dir = args.data_dir / "games"
    if games_dir.exists():
        shutil.rmtree(games_dir)
    game_dir = games_dir / GAME_ID
    game_dir.mkdir(parents=True)

    with ZipFile(args.archive) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise SystemExit(f"Corrupt member in Full Throttle demo ZIP: {corrupt}")

        extracted = 0
        for member in archive.infolist():
            relative = PurePosixPath(member.filename)
            if relative.is_absolute() or ".." in relative.parts:
                raise SystemExit(f"Unsafe path in Full Throttle demo ZIP: {member.filename}")
            if not relative.parts:
                continue
            target = game_dir.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(game_dir.resolve()):
                raise SystemExit(f"ZIP member escapes fixture directory: {member.filename}")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if stat.S_ISLNK(member.external_attr >> 16):
                raise SystemExit(f"Refusing symlink in Full Throttle demo ZIP: {member.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as destination:
                shutil.copyfileobj(source, destination)
            extracted += 1

    if not (game_dir / "FT.000").is_file() or not (game_dir / "FT.001").is_file():
        raise SystemExit("Full Throttle demo ZIP is missing FT.000 or FT.001")

    write_index(games_dir / "index.json", {GAME_ID: {}})
    write_directory_indexes(game_dir)
    print(f"Prepared {GAME_ID}: {extracted} files, SHA-256 {actual_sha}")


if __name__ == "__main__":
    main()
