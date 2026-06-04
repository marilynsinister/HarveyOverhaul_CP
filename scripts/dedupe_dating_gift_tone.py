#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove «солнышко» from most Dating gift lines (keep a few)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "assets/Code/dialogues/harvey_gifts.json"

KEEP_SOLNYSHKO = {
    "AcceptBirthdayGift_Positive",
    "AcceptGift_(O)395",
    "AcceptGift_(O)432",
    "AcceptGift_(O)StardropTea",
    "AcceptGift_(O)348",
}

PREFIX_PET = re.compile(r"^([А-Яа-яЁё][^,?…]*?), солнышко([?.])", re.U)
MID_PET = re.compile(r"Спасибо, солнышко\.", re.U)


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


def soften(text: str, key: str) -> str:
    if key in KEEP_SOLNYSHKO:
        return text
    text = PREFIX_PET.sub(r"\1\2", text)
    text = MID_PET.sub("Спасибо.", text)
    text = text.replace(", солнышко?", "?")
    text = text.replace(", солнышко.", ".")
    return text


def main() -> None:
    raw = PATH.read_text(encoding="utf-8")
    data = json.loads(strip_comments(raw))
    n = 0
    for change in data["Changes"]:
        if change.get("When") != {"Relationship:Harvey": "Dating"}:
            continue
        for key, val in change["Entries"].items():
            if not key.startswith("Accept"):
                continue
            new = soften(val, key)
            if new != val:
                change["Entries"][key] = new
                n += 1
    # Re-use apply formatter
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "apply", Path(__file__).with_name("apply_gift_reactions_split.py")
    )
    apply = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(apply)
    comments = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]
    apply.save_json(PATH, data, comments[:3] if comments else [])
    print(f"Softened {n} dating gift lines.")


if __name__ == "__main__":
    main()
