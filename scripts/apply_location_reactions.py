#!/usr/bin/env python3
"""Apply dangerous-location dialogue patches."""
from __future__ import annotations

import json
from pathlib import Path

from location_reactions_data import (
    DATING,
    HEARTS_67,
    HOSPITAL_STRICT_LOC,
    LOC_47,
    LOC_810,
    LOC_FORMAL,
    MARRIED,
)

ROOT = Path(__file__).resolve().parents[1]


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


def patch_entries(entries: dict, updates: dict) -> list[str]:
    changed = []
    for k, v in updates.items():
        if k in entries:
            entries[k] = v
            changed.append(k)
        else:
            entries[k] = v
            changed.append(k)
    return changed


def apply_locations() -> list[str]:
    path = ROOT / "assets/Code/dialogues/harvey_locations.json"
    changes, notes = load_changes(path)
    all_changed: list[str] = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        w = ch.get("When")
        hearts = (w or {}).get("Hearts:Harvey")
        if w is None:
            upd = LOC_FORMAL
        elif hearts == "4,5,6,7":
            upd = LOC_47
        elif hearts == "8,9,10":
            upd = LOC_810
        else:
            continue
        all_changed.extend(patch_entries(ch["Entries"], upd))
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(path, header, rest, changes)
    return sorted(set(all_changed))


def apply_hearts_35() -> list[str]:
    path = ROOT / "assets/Code/dialogues/harvey_hearts_3_5.json"
    changes, notes = load_changes(path)
    changed: list[str] = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        hearts = (ch.get("When") or {}).get("Hearts:Harvey")
        if hearts in ("4,5,6,7",):
            for k in ("Desert4", "Beach4"):
                if k in ch["Entries"] and k in LOC_47:
                    ch["Entries"][k] = LOC_47[k]
                    changed.append(k)
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(path, header, rest, changes)
    return sorted(set(changed))


def apply_hearts_67() -> list[str]:
    path = ROOT / "assets/Code/dialogues/harvey_hearts_6_7.json"
    changes, notes = load_changes(path)
    changed: list[str] = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        changed.extend(patch_entries(ch["Entries"], HEARTS_67))
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(path, header, rest, changes)
    return sorted(set(changed))


def apply_dating() -> list[str]:
    path = ROOT / "assets/Code/dialogues/harvey_dating.json"
    changes, notes = load_changes(path)
    changed: list[str] = []
    for ch in changes:
        if ch.get("When", {}).get("Relationship:Harvey") == "Dating":
            changed.extend(patch_entries(ch["Entries"], DATING))
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(path, header, rest, changes)
    return sorted(set(changed))


def apply_married() -> list[str]:
    path = ROOT / "assets/Code/dialogues/harvey_married.json"
    changes, notes = load_changes(path)
    changed: list[str] = []
    for ch in changes:
        if ch.get("When", {}).get("Relationship:Harvey") == "Married" and "LocationName" not in ch.get("When", {}):
            if ch.get("Target") == "Characters/Dialogue/MarriageDialogueHarvey":
                changed.extend(patch_entries(ch["Entries"], MARRIED))
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(path, header, rest, changes)
    return sorted(set(changed))


def apply_hospital() -> list[str]:
    path = ROOT / "assets/Code/dialogues/harvey_hospital.json"
    changes, notes = load_changes(path)
    changed: list[str] = []
    for ch in changes:
        hearts = (ch.get("When") or {}).get("Hearts:Harvey")
        if hearts == "6,7,8,9,10":
            for k, v in HOSPITAL_STRICT_LOC.items():
                if k in ch["Entries"]:
                    ch["Entries"][k] = v
                    changed.append(k)
    header = notes[0] if notes else ""
    rest = notes[1:] if len(notes) > 1 else []
    save_changes(path, header, rest, changes)
    return sorted(set(changed))


def main() -> None:
    reports = {
        "harvey_locations.json": apply_locations(),
        "harvey_hearts_3_5.json": apply_hearts_35(),
        "harvey_hearts_6_7.json": apply_hearts_67(),
        "harvey_dating.json": apply_dating(),
        "harvey_married.json": apply_married(),
        "harvey_hospital.json": apply_hospital(),
    }
    all_keys: set[str] = set()
    for fn, keys in reports.items():
        print(f"\n{fn} ({len(keys)}):")
        for k in keys:
            print(f"  {k}")
            all_keys.add(k)
    print(f"\nTotal unique keys: {len(all_keys)}")


if __name__ == "__main__":
    main()
