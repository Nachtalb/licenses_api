#!/usr/bin/env python3
"""Fetch license files from choosealicense.com and generate licenses.json."""

import json
import os
import re
import urllib.request
from pathlib import Path

REPO_API = "https://api.github.com/repos/github/choosealicense.com/contents/_licenses"
DATA_DIR = Path(__file__).parent.parent / "data"
LICENSES_DIR = DATA_DIR / "licenses"
OUTPUT = DATA_DIR / "licenses.json"


def fetch_file_list():
    """Get list of license files from GitHub API."""
    req = urllib.request.Request(REPO_API, headers={"User-Agent": "licenses-fetcher"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def download_file(url: str) -> str:
    """Download a raw file from GitHub."""
    req = urllib.request.Request(url, headers={"User-Agent": "licenses-fetcher"})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode()


def parse_yaml_value(value: str):
    """Parse a simple YAML scalar value."""
    value = value.strip()
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value == "":
        return None
    # Strip quotes
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and return (metadata, content)."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    yaml_text = parts[1].strip()
    content = parts[2].strip()
    meta = {}

    lines = yaml_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Skip empty lines and comments
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue

        # Check for key: value
        match = re.match(r"^(\w[\w-]*)\s*:\s*(.*)", line)
        if not match:
            i += 1
            continue

        key = match.group(1)
        value = match.group(2).strip()

        # Check if next lines are list items or dict items
        if value == "" or value is None:
            # Could be a list or dict — peek ahead
            collected_list = []
            collected_dict = {}
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if not next_line.strip():
                    j += 1
                    continue
                list_match = re.match(r"^\s+-\s+(.*)", next_line)
                dict_match = re.match(r"^\s+(\S[\w\s.-]*\S?)\s*:\s*(.*)", next_line)
                if list_match:
                    collected_list.append(list_match.group(1).strip())
                    j += 1
                elif dict_match:
                    collected_dict[dict_match.group(1).strip()] = parse_yaml_value(
                        dict_match.group(2)
                    )
                    j += 1
                else:
                    break
            if collected_list:
                meta[key] = collected_list
            elif collected_dict:
                meta[key] = collected_dict
            else:
                meta[key] = None
            i = j
        else:
            meta[key] = parse_yaml_value(value)
            i += 1

    return meta, content


def process_license(meta: dict, content: str) -> dict | None:
    """Convert parsed license data to output format."""
    if meta.get("hidden", False):
        return None

    return {
        "spdx_id": meta.get("spdx-id", ""),
        "title": meta.get("title", ""),
        "nickname": meta.get("nickname"),
        "description": meta.get("description", ""),
        "how": meta.get("how", ""),
        "note": meta.get("note"),
        "using": meta.get("using", {}),
        "permissions": meta.get("permissions", []),
        "conditions": meta.get("conditions", []),
        "limitations": meta.get("limitations", []),
        "content": content,
        "hidden": meta.get("hidden", False),
        "featured": meta.get("featured", False),
    }


def main():
    LICENSES_DIR.mkdir(parents=True, exist_ok=True)

    print("Fetching file list from GitHub...")
    files = fetch_file_list()
    txt_files = [f for f in files if f["name"].endswith(".txt")]
    print(f"Found {len(txt_files)} license files")

    licenses = []
    for i, f in enumerate(txt_files, 1):
        name = f["name"]
        print(f"  [{i}/{len(txt_files)}] {name}")

        # Download and save raw file
        raw = download_file(f["download_url"])
        (LICENSES_DIR / name).write_text(raw)

        # Parse
        meta, content = parse_frontmatter(raw)
        license_data = process_license(meta, content)
        if license_data:
            licenses.append(license_data)

    # Sort by title
    licenses.sort(key=lambda x: x["title"].lower())

    # Write JSON
    OUTPUT.write_text(json.dumps(licenses, indent=2, ensure_ascii=False))
    print(f"\nWrote {len(licenses)} licenses to {OUTPUT}")


if __name__ == "__main__":
    main()
