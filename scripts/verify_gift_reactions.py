#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify ty/Вы rules in gift reaction JSON files."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUES = ROOT / "assets/Code/dialogues"

GIFT_KEY_RE = re.compile(
    r"^Accept(?:Gift|BirthdayGift)_|"
    r"^Reject(?:Gift|Item|Bouquet|MermaidPendant|MovieTicket|RoommateProposal)_|"
    r"^AcceptBouquet$|"
    r"^MovieInvitation$|"
    r"^FlowerDance_"
)

TY_RE = re.compile(
    r"\b(ты|тебя|тебе|тобой|тобою|твой|твоя|твоё|твоего|твоей|твоим|твоих|твою)\b",
    re.I,
)
VY_RE = re.compile(r"\b(Вы|Вас|Вам|Ваш|Ваши|Вашего|Вашей)\b")


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


def iter_gift_entries(path: Path):
    data = json.loads(strip_comments(path.read_text(encoding="utf-8")))
    for change in data["Changes"]:
        when = change.get("When", {})
        for key, text in change.get("Entries", {}).items():
            if GIFT_KEY_RE.match(key):
                yield when, key, text


def main() -> int:
    errors = []
    files = [
        (DIALOGUES / "harvey_hearts_0_2.json", "s0", TY_RE, "ты"),
        (DIALOGUES / "harvey_hearts_3_5.json", "s1", None, None),
        (DIALOGUES / "harvey_gifts.json", "s2", None, None),
    ]
    for path, label, bad_re, bad_name in files:
        if not path.exists():
            continue
        for when, key, text in iter_gift_entries(path):
            if label == "s0" and when.get("Hearts:Harvey") in ("0,1,2", None):
                if bad_re and bad_re.search(text):
                    errors.append(f"{path.name} [{key}]: found {bad_name}")
            if when.get("Relationship:Harvey") in ("Dating", "Married"):
                if VY_RE.search(text):
                    errors.append(f"{path.name} [{key}] {when}: found Вы-form")

    # Explicit dating / married blocks in harvey_gifts
    for when, key, text in iter_gift_entries(DIALOGUES / "harvey_gifts.json"):
        rel = when.get("Relationship:Harvey")
        if rel in ("Dating", "Married") and VY_RE.search(text):
            errors.append(f"harvey_gifts.json [{key}] {rel}: found Вы-form")

    if errors:
        print("FAIL:")
        for e in errors:
            print(" ", e)
        return 1
    print("OK: no ty in 0-2 gift blocks; no Вы in Dating/Married gift blocks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
