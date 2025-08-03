#!/usr/bin/env python3
"""Update scummvm-icons XML files using metadata overrides."""

import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Optional, Tuple
import xml.dom.minidom
import xml.etree.ElementTree as ET

METADATA_PATH = Path(__file__).parent.parent / "assets" / "metadata.json"
GAMES_XML_PATH = Path(__file__).parent.parent / "scummvm-icons" / "games.xml"
COMPANIES_XML_PATH = Path(__file__).parent.parent / "scummvm-icons" / "companies.xml"

GAME_ATTR_ORDER = (
    "id",
    "name",
    "engine_id",
    "company_id",
    "year",
    "moby_id",
    "steam_id",
    "gog_id",
    "zoom_id",
    "additional_stores",
    "datafiles",
    "wikipedia_page",
    "series_id",
)


def load_metadata(metadata_path: Path) -> Dict[str, Dict[str, object]]:
    if not metadata_path.exists():
        return {}
    with open(metadata_path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    result: Dict[str, Dict[str, object]] = {}
    for relative_path, entry in raw.items():
        if not isinstance(entry, dict):
            continue
        entry_copy = entry.copy()
        entry_copy.setdefault("relative_path", relative_path)
        result[relative_path] = entry_copy
    return result


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "", value.lower())
    return slug or "company"


def load_xml(path: Path) -> ET.ElementTree:
    tree = ET.parse(path)
    return tree


def build_company_indices(companies_root: ET.Element) -> Tuple[Dict[str, ET.Element], Dict[str, str]]:
    by_id: Dict[str, ET.Element] = {}
    by_name: Dict[str, str] = {}
    for company in companies_root.findall("company"):
        company_id = company.get("id", "")
        name = company.get("name", "")
        if company_id:
            by_id[company_id] = company
        if name:
            by_name[name.lower()] = company_id
    return by_id, by_name


def ensure_company(companies_root: ET.Element, companies_by_id: Dict[str, ET.Element], companies_by_name: Dict[str, str], company_name: str) -> str:
    key = company_name.strip()
    if not key:
        return ""

    existing_id = companies_by_name.get(key.lower())
    if existing_id:
        return existing_id

    candidate_id = slugify(key)
    suffix = 1
    unique_id = candidate_id
    while unique_id in companies_by_id:
        suffix += 1
        unique_id = f"{candidate_id}{suffix}"

    new_company = ET.Element("company", OrderedDict([
        ("id", unique_id),
        ("name", key),
        ("alt_name", ""),
    ]))
    companies_root.append(new_company)
    companies_by_id[unique_id] = new_company
    companies_by_name[key.lower()] = unique_id
    return unique_id


def build_game_index(games_root: ET.Element) -> Dict[str, ET.Element]:
    result: Dict[str, ET.Element] = {}
    for game in games_root.findall("game"):
        game_id = game.get("id", "")
        if game_id:
            result[game_id] = game
    return result


def update_game_element(game: ET.Element, attributes: Dict[str, str]) -> None:
    for key in GAME_ATTR_ORDER:
        if key in attributes and attributes[key] is not None:
            game.set(key, attributes[key])


def create_game_element(attributes: Dict[str, str]) -> ET.Element:
    ordered = OrderedDict((key, attributes.get(key, "")) for key in GAME_ATTR_ORDER)
    return ET.Element("game", ordered)


def write_pretty_xml(root: ET.Element, destination: Path) -> None:
    dom = xml.dom.minidom.parseString(ET.tostring(root).decode("utf-8"))
    with open(destination, "w", encoding="utf-8") as handle:
        handle.write(dom.toprettyxml())


def main() -> int:
    parser = argparse.ArgumentParser(description="Adjust scummvm-icons XML files using metadata overrides.")
    parser.add_argument("--metadata", default=str(METADATA_PATH), help="Path to metadata.json")
    parser.add_argument("--games-xml", default=str(GAMES_XML_PATH), help="Path to scummvm-icons/games.xml")
    parser.add_argument("--companies-xml", default=str(COMPANIES_XML_PATH), help="Path to scummvm-icons/companies.xml")
    args = parser.parse_args()

    metadata = load_metadata(Path(args.metadata))
    if not metadata:
        print("No metadata entries found; nothing to adjust.")
        return 0

    games_tree = load_xml(Path(args.games_xml))
    companies_tree = load_xml(Path(args.companies_xml))

    games_root = games_tree.getroot()
    companies_root = companies_tree.getroot()

    games_by_id = build_game_index(games_root)
    companies_by_id, companies_by_name = build_company_indices(companies_root)

    for metadata_entry in metadata.values():
        if metadata_entry.get("skip") is True:
            continue
        full_id = metadata_entry.get("id")
        if not full_id or ":" not in full_id:
            continue

        engine_id, game_id = full_id.split(":", maxsplit=1)
        if not game_id:
            continue

        game_attributes: Dict[str, Optional[str]] = {
            "id": game_id,
            "engine_id": engine_id,
        }

        metadata_name = metadata_entry.get("name")
        if isinstance(metadata_name, str) and metadata_name.strip():
            game_attributes["name"] = metadata_name.strip()

        company_name = metadata_entry.get("company")
        if isinstance(company_name, str) and company_name.strip():
            company_id = ensure_company(companies_root, companies_by_id, companies_by_name, company_name)
            if company_id:
                game_attributes["company_id"] = company_id

        existing_game = games_by_id.get(game_id)
        if existing_game is None:
            new_game = create_game_element({key: game_attributes.get(key, "") for key in GAME_ATTR_ORDER})
            games_root.append(new_game)
            games_by_id[game_id] = new_game
        else:
            update_game_element(existing_game, {key: game_attributes.get(key) for key in GAME_ATTR_ORDER})

    games_root[:] = sorted(games_root, key=lambda elem: elem.get("id", ""))
    companies_root[:] = sorted(companies_root, key=lambda elem: elem.get("id", ""))

    write_pretty_xml(games_root, Path(args.games_xml))
    write_pretty_xml(companies_root, Path(args.companies_xml))

    print("Updated games.xml and companies.xml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
