#!/usr/bin/env python3
"""Diff reaction keys in split files vs HEAD dialoguesHarvey.json."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = re.compile(
    r"^(?:"
    r"Hospital(?:_(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Entry)|\d?|2|4|6|8|10)?"
    r"|timeReaction_"
    r"|locationReaction_"
    r"|emotionalReaction_"
    r"|situationReaction_"
    r"|GreenRain"
    r"|topicHarvey"
    r"|Treat_Hurt_"
    r"|eventSeen_eventHarveyFirstWalk_"
    r")"
)


def strip_comments(text: str) -> str:
    out, i, in_str, escape = [], 0, False, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def load_entries(path_or_text: str | Path) -> list[tuple[dict | None, str, str]]:
    if isinstance(path_or_text, Path):
        raw = path_or_text.read_text(encoding="utf-8")
    else:
        raw = path_or_text
    data = json.loads(strip_comments(raw))
    rows: list[tuple[dict | None, str, str]] = []
    for ch in data["Changes"]:
        if ch.get("Action") not in ("EditData", "Include"):
            continue
        if ch.get("Target") != "Characters/Dialogue/Harvey":
            continue
        w = ch.get("When")
        for k, v in ch.get("Entries", {}).items():
            rows.append((w, k, v))
    return rows


def main() -> None:
    old_raw = subprocess.check_output(
        ["git", "-C", str(ROOT), "show", "HEAD:assets/Code/dialoguesHarvey.json"],
        text=True,
        errors="replace",
    )
    old_rows = load_entries(old_raw)
    old_map: dict[tuple[str, str], str] = {}
    for w, k, v in old_rows:
        if not PATTERN.match(k):
            continue
        key = (json.dumps(w, sort_keys=True) if w else "", k)
        old_map[key] = v

    files = [
        "harvey_locations.json",
        "harvey_hospital.json",
        "harvey_topics_medical.json",
    ]
    all_changed: list[str] = []
    samples: list[str] = []
    for fn in files:
        for w, k, v in load_entries(ROOT / "assets/Code/dialogues" / fn):
            if not PATTERN.match(k):
                continue
            key = (json.dumps(w, sort_keys=True) if w else "", k)
            old_v = old_map.get(key)
            if old_v == v:
                continue
            all_changed.append(f"{fn}:{k}:{w or 'default'}")
            if len(samples) < 10:
                samples.append(
                    f"### {fn} — `{k}`\nWhen: `{w}`\n\n**Было:**\n{old_v or '—'}\n\n**Стало:**\n{v}\n"
                )

    keys_out = ROOT / "docs" / "_harvey_reactions_changed_keys.txt"
    keys_out.write_text("\n".join(sorted(all_changed)), encoding="utf-8")
    diff_out = ROOT / "docs" / "_harvey_reactions_diff_samples.md"
    diff_out.write_text("\n".join(samples), encoding="utf-8")
    print(f"Changed: {len(all_changed)}")
    print(f"Keys: {keys_out}")
    print(f"Samples: {diff_out}")


if __name__ == "__main__":
    main()
