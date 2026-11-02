#!/usr/bin/env python3
import json
import subprocess
from collections import Counter
from pathlib import Path

FILES = ("posuto/postaldata.json", "posuto/officedata.json")


def load_from_git(ref, path):
    proc = subprocess.run(["git", "show", f"{ref}:{path}"], text=True, capture_output=True)
    return json.loads(proc.stdout) if proc.returncode == 0 else {}


def summarize(before, after):
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in set(before) & set(after) if before[k] != after[k])
    prefectures = Counter()
    for key in added + changed:
        row = after[key]
        prefectures[row.get("prefecture", "不明")] += 1
    for key in removed:
        row = before[key]
        prefectures[row.get("prefecture", "不明")] += 1
    return added, removed, changed, prefectures


lines = ["## Japan Post data update", "", "| Dataset | Added | Removed | Changed |", "|---|---:|---:|---:|"]
total = Counter()
for path in FILES:
    before = load_from_git("HEAD", path)
    after = json.loads(Path(path).read_text())
    added, removed, changed, prefectures = summarize(before, after)
    lines.append(f"| `{path}` | {len(added)} | {len(removed)} | {len(changed)} |")
    total.update(prefectures)
lines += ["", "### Changed records by prefecture", ""]
if total:
    lines += ["| Prefecture | Records |", "|---|---:|"]
    lines += [f"| {name} | {count} |" for name, count in sorted(total.items(), key=lambda item: (-item[1], item[0]))]
else:
    lines.append("No postal records changed.")
Path("update-summary.md").write_text("\n".join(lines) + "\n")
