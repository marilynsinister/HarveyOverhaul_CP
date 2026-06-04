#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reduce overused «котёнок» / «девочка моя» / «солнышко» in Married gift lines."""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "assets/Code/dialogues/harvey_gifts.json"

KEEP_PET = {
    "AcceptBirthdayGift_Positive",
    "AcceptBirthdayGift_Loved",
    "AcceptGift_(O)StardropTea",
    "AcceptGift_(O)201",
}

START_PET = re.compile(
    r"^(Котёнок|Девочка моя|Солнышко),?\s*",
    re.I,
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


def soften(text: str, key: str) -> str:
    if key in KEEP_PET:
        return text
    if START_PET.match(text):
        text = START_PET.sub("", text)
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
    text = text.replace(", солнышко?", "?")
    text = text.replace(", девочка моя?", "?")
    text = text.replace(", котёнок?", "?")
    return text


def main() -> None:
    raw = PATH.read_text(encoding="utf-8")
    data = json.loads(strip_comments(raw))
    n = 0
    for change in data["Changes"]:
        if change.get("When") != {"Relationship:Harvey": "Married"}:
            continue
        for key, val in list(change["Entries"].items()):
            if not key.startswith("Accept"):
                continue
            new = soften(val, key)
            if new != val:
                change["Entries"][key] = new
                n += 1
    spec = importlib.util.spec_from_file_location(
        "apply", Path(__file__).with_name("apply_gift_reactions_split.py")
    )
    apply = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(apply)
    comments = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]
    apply.save_json(PATH, data, comments[:3] if comments else [])
    print(f"Softened {n} married gift lines.")


if __name__ == "__main__":
    main()
