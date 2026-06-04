#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply gift + social reaction tiers to split dialogue JSON files."""
from __future__ import annotations

import importlib.util
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


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gift_data = load_module("gift_data", Path(__file__).with_name("gift_tone_layers.py"))
social_data = load_module("social_data", Path(__file__).with_name("gift_social_layers.py"))
override_data = load_module("override_data", Path(__file__).with_name("gift_tone_overrides.py"))

GIFTS = gift_data.GIFTS
SOCIAL = social_data.SOCIAL
OVERRIDES = override_data.OVERRIDES


def tier_entries(tier: str) -> dict:
    out = {k: v[tier] for k, v in GIFTS.items()}
    for (key, t), text in OVERRIDES.items():
        if t == tier and key in out:
            out[key] = text
    for k, v in SOCIAL.items():
        out[k] = v[tier]
    return out


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


def load_json(path: Path) -> dict:
    return json.loads(strip_comments(path.read_text(encoding="utf-8")))


def save_json(path: Path, data: dict, header_comments: list[str]) -> None:
    lines = ["{"]
    lines.append('  "Changes": [')
    for ci, change in enumerate(data["Changes"]):
        if ci > 0:
            lines.append("    },")
        comment = change.get("_comment")
        if comment:
            lines.append(f"    // {comment}")
        lines.append("    {")
        for key in ("Action", "Target", "Priority"):
            if key in change:
                lines.append(f'      "{key}": {json.dumps(change[key], ensure_ascii=False)},')
        if "When" in change:
            lines.append('      "When": {')
            for wk, wv in change["When"].items():
                lines.append(f'        "{wk}": {json.dumps(wv, ensure_ascii=False)},')
            lines[-1] = lines[-1].rstrip(",")
            lines.append("      },")
        lines.append('      "Entries": {')
        ent_lines = []
        for ek, ev in change["Entries"].items():
            ent_lines.append(f'        "{ek}": {json.dumps(ev, ensure_ascii=False)},')
        if ent_lines:
            ent_lines[-1] = ent_lines[-1].rstrip(",")
        lines.extend(ent_lines)
        lines.append("      }")
    lines.append("    }")
    lines.append("  ]")
    lines.append("}")
    body = "\n".join(lines) + "\n"
    if header_comments:
        prefix = "\n".join(f"// {c}" for c in header_comments) + "\n"
        body = prefix + body
    path.write_text(body, encoding="utf-8")


def merge_entries(entries: dict, tier: str) -> dict:
    patch = tier_entries(tier)
    merged = dict(entries)
    merged.update(patch)
    return merged


def is_gift_block(entries: dict) -> bool:
    return any(GIFT_KEY_RE.match(k) for k in entries)


def patch_file_gift_only(path: Path, tier: str, when_match: dict) -> bool:
    data = load_json(path)
    raw = path.read_text(encoding="utf-8")
    comments = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]
    changed = False
    for change in data["Changes"]:
        when = change.get("When", {})
        if when != when_match:
            continue
        ent = change.get("Entries", {})
        if not is_gift_block(ent):
            continue
        change["Entries"] = merge_entries(ent, tier)
        changed = True
    if changed:
        save_json(path, data, comments[:3] if comments else [])
    return changed


def patch_dating_flower(path: Path) -> None:
    data = load_json(path)
    raw = path.read_text(encoding="utf-8")
    comments = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]
    for change in data["Changes"]:
        if change.get("When") != {"Relationship:Harvey": "Dating"}:
            continue
        ent = change["Entries"]
        if "FlowerDance_Accept" in ent:
            ent["FlowerDance_Accept"] = SOCIAL["FlowerDance_Accept"]["dating"]
    save_json(path, data, comments[:3] if comments else [])


def patch_locations_flowers() -> None:
    path = DIALOGUES / "harvey_locations.json"
    data = load_json(path)
    raw = path.read_text(encoding="utf-8")
    comments = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]
    for change in data["Changes"]:
        when = change.get("When")
        if when is None:
            tier = "s0"
        elif when == {"Hearts:Harvey": "4,5,6,7"}:
            tier = "s1"
        elif when == {"Hearts:Harvey": "8,9,10"}:
            tier = "s2"
        else:
            continue
        ent = change["Entries"]
        for key in ("FlowerDance_Accept", "FlowerDance_Decline"):
            if key in ent and key in SOCIAL:
                ent[key] = SOCIAL[key][tier]
    save_json(path, data, comments[:3] if comments else [])


def add_social_blocks_base() -> None:
    """Tiered social keys override harvey_base.json fallbacks."""
    path = DIALOGUES / "harvey_gifts.json"
    data = load_json(path)
    raw = path.read_text(encoding="utf-8")
    comments = [ln.strip()[2:].strip() for ln in raw.splitlines() if ln.strip().startswith("//")]

    extra = [
        {
            "_comment": "Social gift keys — 0-2 hearts",
            "Action": "EditData",
            "Target": "Characters/Dialogue/Harvey",
            "Priority": "Late",
            "When": {"Hearts:Harvey": "0,1,2"},
            "Entries": {k: v["s0"] for k, v in SOCIAL.items()},
        },
        {
            "_comment": "Social gift keys — 3-5 hearts",
            "Action": "EditData",
            "Target": "Characters/Dialogue/Harvey",
            "Priority": "Late",
            "When": {"Hearts:Harvey": "3,4,5"},
            "Entries": {k: v["s1"] for k, v in SOCIAL.items()},
        },
    ]
    # Avoid duplicate social-only blocks
    existing_when = [c.get("When") for c in data["Changes"]]
    for block in extra:
        if block["When"] in existing_when:
            continue
        data["Changes"].insert(0, block)
    save_json(path, data, comments[:3] if comments else [])


def main() -> None:
    patch_file_gift_only(
        DIALOGUES / "harvey_hearts_0_2.json",
        "s0",
        {"Hearts:Harvey": "0,1,2"},
    )
    patch_file_gift_only(
        DIALOGUES / "harvey_hearts_3_5.json",
        "s1",
        {"Hearts:Harvey": "3,4,5"},
    )
    for when, tier in (
        ({"Hearts:Harvey": "6,7,8,9,10"}, "s2"),
        ({"Relationship:Harvey": "Married"}, "married"),
        ({"Relationship:Harvey": "Dating"}, "dating"),
    ):
        patch_file_gift_only(DIALOGUES / "harvey_gifts.json", tier, when)

    patch_dating_flower(DIALOGUES / "harvey_dating.json")
    patch_locations_flowers()

    print(f"Applied {len(GIFTS)} gift + {len(SOCIAL)} social keys to split files.")


if __name__ == "__main__":
    main()
    for mod_name in ("dedupe_dating_gift_tone", "dedupe_married_gift_tone"):
        spec = importlib.util.spec_from_file_location(
            mod_name, Path(__file__).with_name(f"{mod_name}.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
