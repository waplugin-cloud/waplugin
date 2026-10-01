#!/usr/bin/env python3
"""Build a portable plugin ZIP; use --chatgpt-update for the existing ChatGPT app."""
import argparse
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHATGPT_ID = "app-6aa50863af94819199e0cd3c757827db"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--chatgpt-update", action="store_true")
parser.add_argument("--output", type=Path)
args = parser.parse_args()
manifest = json.loads((ROOT / "plugin.json").read_text())
if args.chatgpt_update:
    manifest["name"] = CHATGPT_ID
name = manifest["name"]
output = args.output or ROOT / "dist" / ("waplugin-chatgpt-update.zip" if args.chatgpt_update else "waplugin.zip")
output.parent.mkdir(parents=True, exist_ok=True)
files = [ROOT / "mcp.json"]
for directory in ("skills", "assets"):
    files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ROOT).parts))
with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
    archive.writestr(name + "/plugin.json", json.dumps(manifest, indent=2) + "\n")
    for path in sorted(files):
        if path.is_symlink():
            raise ValueError(f"Symlink not allowed: {path}")
        archive.write(path, name + "/" + path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(output) as archive:
    if archive.testzip() is not None:
        raise ValueError("ZIP integrity check failed")
print(output.resolve())
