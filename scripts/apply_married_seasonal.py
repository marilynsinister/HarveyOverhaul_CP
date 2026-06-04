#!/usr/bin/env python3
"""Patch married FarmHouse seasonal + formal festival keys."""
from __future__ import annotations

import json
import re
from pathlib import Path

from married_seasonal_data import FORMAL_FESTIVAL_ADD, MARRIED_SEASONAL

ROOT = Path(__file__).resolve().parents[1]
MARRIED = ROOT / "assets/Code/dialogues/harvey_married.json"
LOCATIONS = ROOT / "assets/Code/dialogues/harvey_locations.json"


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


def load_changes(path: Path) -> tuple[list, list[str]]:
    raw = path.read_text(encoding="utf-8")
    notes = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]
    data = json.loads(strip_comments(raw))
    header = notes[0] if notes else ""
    rest = [n for n in notes[1:] if n and n != header]
    return data["Changes"], [header] + rest


def save_changes(path: Path, header: str, notes: list[str], changes: list) -> None:
    lines = ["{", '  "Changes": [']
    lines.append(f"    // {header}")
    for n in notes:
        if n and n != header:
            lines.append(f"    // {n}")
    for i, ch in enumerate(changes):
        block = json.dumps(ch, ensure_ascii=False, indent=2)
        indented = "\n".join("    " + ln for ln in block.splitlines())
        lines.append(indented + ("," if i < len(changes) - 1 else ""))
    lines.append("  ]")
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def patch_married() -> list[str]:
    changes, notes = load_changes(MARRIED)
    changed: list[str] = []
    for ch in changes:
        entries = ch.get("Entries")
        when = ch.get("When", {})
        if not entries:
            continue
        if when.get("Relationship:Harvey") == "Married" and when.get("LocationName") == "FarmHouse":
            for k, v in MARRIED_SEASONAL.items():
                if k in entries:
                    entries[k] = v
                    changed.append(k)
        if when.get("Relationship:Harvey") == "Married" and "LocationName" not in when:
            if "fall_15" in entries:
                entries["fall_15"] = (
                    "Завтра ярмарка.$h#$b#Шум утомляет — знаю. Пойдём, а когда устанешь — домой, по твоему знаку.$0"
                    "#$b#Сладости и тишина вечером.$l"
                )
                changed.append("fall_15")
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(MARRIED, header, rest, changes)
    return sorted(set(changed))


def patch_locations() -> list[str]:
    changes, notes = load_changes(LOCATIONS)
    changed: list[str] = []
    for ch in changes:
        entries = ch.get("Entries")
        if not entries or ch.get("When"):
            continue
        for k, v in FORMAL_FESTIVAL_ADD.items():
            entries[k] = v
            changed.append(k)
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(LOCATIONS, header, rest, changes)
    return sorted(set(changed))


def main() -> None:
    m = patch_married()
    l = patch_locations()
    print(f"married: {len(m)} keys")
    for k in m:
        print(f"  {k}")
    print(f"locations formal: {len(l)} keys")
    for k in l:
        print(f"  {k}")


if __name__ == "__main__":
    main()
