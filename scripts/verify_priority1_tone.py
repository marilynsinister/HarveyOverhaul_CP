#!/usr/bin/env python3
"""Verify tone rules for priority 1 additions."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "assets/Code/dialogues/harvey_locations.json",
    ROOT / "assets/Code/dialogues/harvey_hospital.json",
    ROOT / "assets/Code/dialogues/harvey_dating.json",
    ROOT / "assets/Code/dialogues/harvey_married.json",
    ROOT / "assets/Code/dialogues/harvey_topics_medical.json",
    ROOT / "assets/Code/dialogues/harvey_priority2.json",
]

VY = re.compile(r"\b(Вы|Вас|Вам|Ваш|Ваше|Ваши)\b")
TY = re.compile(r"\b(ты|тебя|тебе|твой|твоё|твоя)\b", re.I)
PET = re.compile(r"(солнышко|малышк|котёнок|котенок|девочка моя)", re.I)

KEYS = {
    "timeReaction_Late", "timeReaction_VeryLate", "timeReaction_Early",
    "locationReaction_Mine", "locationReaction_SkullCave",
    "situationReaction_Exhausted", "situationReaction_Injured",
    "emotionalReaction_Crying", "emotionalReaction_Scared",
} | {f"Hospital_{d}" for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")}


def strip_comments(text: str) -> str:
    out, i, in_str, esc = [], 0, False, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            esc = not esc and c == "\\"
            if not esc and c == '"':
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


def hearts(when):
    if not when:
        return None
    h = when.get("Hearts:Harvey")
    return set(int(x) for x in str(h).split(",")) if h else None


def main():
    errors = []
    for path in FILES:
        data = json.loads(strip_comments(path.read_text(encoding="utf-8")))
        for ch in data.get("Changes", []):
            when = ch.get("When") or {}
            rel = when.get("Relationship:Harvey")
            hs = hearts(when)
            for key, text in (ch.get("Entries") or {}).items():
                if not (key in KEYS or key.startswith("topicHarvey")):
                    continue
                if hs and hs <= {0, 1, 2}:
                    if TY.search(text):
                        errors.append(f"{path.name} {key} 0-2: ty found")
                    if PET.search(text):
                        errors.append(f"{path.name} {key} 0-2: pet name")
                if rel in ("Dating", "Married") or (hs and min(hs) >= 3):
                    if rel in ("Dating", "Married") and VY.search(text):
                        errors.append(f"{path.name} {key} {rel}: Vy found")
    if errors:
        print("FAIL:", len(errors))
        for e in errors[:30]:
            print(" ", e)
    else:
        print("OK: no tone violations in new priority-1 patches")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
