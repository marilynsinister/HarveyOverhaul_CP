#!/usr/bin/env python3
"""Rewrite reaction dialogue in three split files — run to apply."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from rewrite_harvey_reactions_data import (
    HOSPITAL_47,
    HOSPITAL_810,
    HOSPITAL_DATING,
    HOSPITAL_ENTRY,
    HOSPITAL_STRICT,
    LOC_47,
    LOC_810,
    LOC_FORMAL,
    TOPICS_DATING,
    TOPICS_FORMAL,
)

ROOT = Path(__file__).resolve().parents[1]

REWRITE_KEY = re.compile(
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


def load_changes(path: Path) -> tuple[list, list[str]]:
    raw = path.read_text(encoding="utf-8")
    notes = []
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("//") and not s.startswith("// "):
            pass
        if s.startswith("//"):
            notes.append(s[2:].strip())
    data = json.loads(strip_comments(raw))
    header = notes[0] if notes else ""
    rest = [n for n in notes[1:] if n]
    return data["Changes"], [header] + rest


def save_changes(path: Path, header: str, notes: list[str], changes: list):
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


def when_sig(when: dict | None) -> str:
    if not when:
        return ""
    return json.dumps(when, sort_keys=True)


def count_entries(changes: list) -> int:
    return sum(
        len(c.get("Entries", {}))
        for c in changes
        if c.get("Action") == "EditData"
    )


def patch_map(changes: list, tier: str, updates: dict, full_patch: bool) -> list[str]:
    changed = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        entries = ch["Entries"]
        for key, value in updates.items():
            if key not in entries:
                continue
            if full_patch or REWRITE_KEY.match(key):
                entries[key] = value
                changed.append(key)
    return changed


def apply_locations(changes: list) -> list[str]:
    all_changed = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        w = ch.get("When")
        hearts = (w or {}).get("Hearts:Harvey")
        if w is None:
            upd, full = LOC_FORMAL, True
        elif hearts == "4,5,6,7":
            upd, full = LOC_47, True
        elif hearts == "8,9,10":
            upd, full = LOC_810, True
        else:
            continue
        for k in upd:
            if k in ch["Entries"]:
                ch["Entries"][k] = upd[k]
                all_changed.append(k)
    return sorted(set(all_changed))


def apply_hospital(changes: list) -> list[str]:
    all_changed = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        w = ch.get("When") or {}
        if not w:
            upd = HOSPITAL_ENTRY
        elif w.get("Hearts:Harvey") == "6,7,8,9,10":
            upd = HOSPITAL_STRICT
        elif w.get("Hearts:Harvey") == "4,5,6,7":
            upd = HOSPITAL_47
        elif w.get("Hearts:Harvey") == "8,9,10":
            upd = HOSPITAL_810
        elif w.get("Relationship:Harvey") == "Dating":
            upd = HOSPITAL_DATING
        else:
            continue
        for k, v in upd.items():
            if k in ch["Entries"]:
                ch["Entries"][k] = v
                all_changed.append(k)
    return sorted(set(all_changed))


def apply_topics(changes: list) -> list[str]:
    all_changed = []
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        w = ch.get("When")
        if w is None:
            upd = TOPICS_FORMAL
        elif w.get("Relationship:Harvey") == "Dating":
            upd = TOPICS_DATING
        else:
            # Other patches: only pattern keys if present in upd-like sets
            continue
        for k, v in upd.items():
            if k in ch["Entries"]:
                ch["Entries"][k] = v
                all_changed.append(k)
        # Pattern-only pass for trauma/first meeting/exhaustion/walk patches
        if w is not None:
            for k in list(ch["Entries"]):
                if not REWRITE_KEY.match(k):
                    continue
                # keep existing unless we add explicit overrides later
    return sorted(set(all_changed))


EXPECTED = {
    "harvey_locations.json": 199,
    "harvey_hospital.json": 52,
    "harvey_topics_medical.json": 193,
}


def verify_counts(root: Path) -> bool:
    ok = True
    for fn, expected in EXPECTED.items():
        path = root / "assets/Code/dialogues" / fn
        d = json.loads(strip_comments(path.read_text(encoding="utf-8")))
        n = count_entries(d["Changes"])
        match = n == expected
        print(f"{fn}: entries={n} expected={expected} {'OK' if match else 'FAIL'}")
        ok = ok and match
    return ok


def main() -> int:
    files = {
        "harvey_locations.json": apply_locations,
        "harvey_hospital.json": apply_hospital,
        "harvey_topics_medical.json": apply_topics,
    }
    report: dict[str, list[str]] = {}
    for fn, apply_fn in files.items():
        path = ROOT / "assets/Code/dialogues" / fn
        changes, notes = load_changes(path)
        before = count_entries(changes)
        header = notes[0] if notes else ""
        rest = notes[1:] if len(notes) > 1 else []
        changed = apply_fn(changes)
        after = count_entries(changes)
        if before != after:
            print(f"ERROR {fn}: entry count {before} -> {after}")
            return 1
        save_changes(path, header, rest, changes)
        report[fn] = changed
        print(f"{fn}: {len(changed)} keys updated")

    print("\n=== Changed keys ===")
    for fn, keys in report.items():
        print(f"\n{fn} ({len(keys)}):")
        for k in keys:
            print(f"  {k}")

    print("\n=== Intentionally strict (unchanged by design) ===")
    print("  topicHarvey_Neglect (formal 0-2) — firm tone kept")
    print("  HOSPITAL_STRICT tier — clinical firmness without romance/control pet names")

    if not verify_counts(ROOT):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
