#!/usr/bin/env python3
"""Split dialoguesHarvey.json into include files — preserves separate Change blocks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "Code" / "dialoguesHarvey.json"
OUT_DIR = ROOT / "assets" / "Code" / "dialogues"

LOAD_ORDER = [
    ("harvey_schedule_strings.json", "schedule"),
    ("harvey_base.json", "base"),
    ("harvey_hearts_0_2.json", "hearts_0_2"),
    ("harvey_hearts_3_5.json", "hearts_3_5"),
    ("harvey_hearts_6_7.json", "hearts_6_7"),
    ("harvey_topics_medical.json", "topics_medical"),
    ("harvey_locations.json", "locations"),
    ("harvey_hospital.json", "hospital"),
    ("harvey_gifts.json", "gifts"),
    ("harvey_dating.json", "dating"),
    ("harvey_married.json", "married"),
    ("harvey_priority2.json", "priority2"),
]

BLOCK_HEADERS = {
    1: "Schedule — default",
    2: "Schedule — married",
    3: "Base layer (no When)",
    4: "Strict hospital 6–10 hearts",
    5: "Hearts 4–7 (effective When from duplicate field)",
    6: "Hearts 8–10 friendship",
    7: "Gifts 0–2",
    8: "Gifts 3–5",
    9: "Gifts 6–10 pre-dating",
    10: "Gifts married",
    11: "Relationship Dating (split by key type)",
    12: "MarriageDialogueHarvey",
    31: "Visit topics (no When) — end of source",
}


def strip_comments(text: str) -> str:
    out = []
    i = 0
    in_str = False
    escape = False
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


def make_patch(
    target: str,
    entries: dict,
    when: dict | None = None,
    priority: str = "Late",
) -> dict:
    p: dict = {
        "Action": "EditData",
        "Target": target,
        "Priority": priority,
        "Entries": entries,
    }
    if when:
        p["When"] = when
    return p


def append_patch(buckets: dict, bucket: str, patch: dict, stats: dict, keys: list[str]):
    buckets.setdefault(bucket, []).append(patch)
    stats.setdefault(bucket, []).extend(keys)


def is_gift_key(k: str) -> bool:
    return k.startswith("AcceptGift_") or k.startswith("AcceptBirthdayGift_")


def is_topic_key(k: str) -> bool:
    return k.startswith("topicHarvey") or k.startswith("Treat_Hurt_")


def is_hospital_key(k: str) -> bool:
    if re.match(r"^Hospital_(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Entry)$", k):
        return True
    if k in ("Hospital", "Hospital2", "Hospital4", "Hospital6", "Hospital8", "Hospital10"):
        return True
    return False


def is_location_key(k: str) -> bool:
    if k.startswith(
        (
            "timeReaction_",
            "locationReaction_",
            "emotionalReaction_",
            "situationReaction_",
            "Resort",
        )
    ):
        return True
    if re.match(r"^(Saloon|Desert|Beach|HarveyRoom|ArchaeologyHouse)", k):
        return True
    if re.match(r"^(Spring|Summer|Fall|Winter)_\d+$", k):
        return True
    if re.match(r"^(spring|summer|fall|winter)_", k):
        return True
    if k in (
        "Town",
        "Saloon",
        "Beach",
        "ArchaeologyHouse",
        "Mountain",
        "GreenRain",
        "GreenRain_2",
        "FlowerDance_Accept",
        "FlowerDance_Decline",
        "summer_9",
        "winter_30",
    ):
        return True
    if re.match(r"^(spring|summer|fall|winter)_\d+$", k):
        return True
    return False


def heart_tier_suffix(k: str) -> int | None:
    m = re.search(r"(\d+)$", k)
    if not m:
        return None
    n = int(m.group(1))
    if n in (2, 4, 6, 8, 10):
        return n
    return None


def classify_base_key(k: str) -> str:
    if is_topic_key(k):
        return "topics_medical"
    if is_gift_key(k):
        return "gifts"
    if is_hospital_key(k):
        return "hospital"
    if is_location_key(k):
        return "locations"
    return "base"


def classify_hearts_457_key(k: str) -> str:
    if is_gift_key(k):
        return "gifts"
    if is_hospital_key(k):
        return "hospital"
    if heart_tier_suffix(k) == 6:
        return "hearts_6_7"
    if heart_tier_suffix(k) == 4:
        return "hearts_3_5"
    return "locations"


def classify_hearts_810_key(k: str) -> str:
    if is_gift_key(k):
        return "gifts"
    if is_hospital_key(k):
        return "hospital"
    return "locations"


def classify_dating_key(k: str) -> str:
    if is_gift_key(k):
        return "gifts"
    if is_hospital_key(k):
        return "hospital"
    if k.startswith("topicHarvey"):
        return "topics_medical"
    return "dating"


def split_block(
    target: str,
    when: dict | None,
    entries: dict,
    classifier,
    buckets: dict,
    stats: dict,
    header_suffix: str = "",
):
    groups: dict[str, dict] = {}
    for k, v in entries.items():
        b = classifier(k)
        groups.setdefault(b, {})[k] = v
    for b, sub in groups.items():
        if not sub:
            continue
        append_patch(
            buckets,
            b,
            make_patch(target, sub, when),
            stats,
            list(sub.keys()),
        )


def write_bucket_file(path: Path, header: str, patches: list[dict], block_notes: list[str]):
    lines = ["{", '  "Changes": [']
    if header:
        lines.append(f"    // {header}")
    for note in block_notes:
        lines.append(f"    // {note}")
    for i, p in enumerate(patches):
        block = json.dumps(p, ensure_ascii=False, indent=2)
        indented = "\n".join("    " + ln for ln in block.splitlines())
        lines.append(indented + ("," if i < len(patches) - 1 else ""))
    lines.append("  ]")
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    data = json.loads(strip_comments(SRC.read_text(encoding="utf-8")))
    changes = data["Changes"]
    buckets: dict[str, list] = {}
    stats: dict[str, list[str]] = {}
    block_notes: dict[str, list[str]] = {b: [] for _, b in LOAD_ORDER}

    idx = 0
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        idx += 1
        target = ch["Target"]
        when = ch.get("When")
        entries = ch.get("Entries") or {}
        note = BLOCK_HEADERS.get(idx, f"Source block #{idx}")

        if idx in (1, 2):
            b = "schedule"
            block_notes[b].append(note)
            append_patch(buckets, b, make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 3:
            block_notes["base"].append(note + " — split by key type")
            split_block(target, when, entries, classify_base_key, buckets, stats)
        elif idx == 4:
            block_notes["hospital"].append(note)
            append_patch(buckets, "hospital", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 5:
            block_notes["locations"].append(note + " — location keys")
            block_notes["hearts_6_7"].append(note + " — *6 keys")
            block_notes["hearts_3_5"].append(note + " — *4 keys")
            block_notes["hospital"].append(note + " — Hospital_*")
            split_block(target, when, entries, classify_hearts_457_key, buckets, stats)
        elif idx == 6:
            block_notes["locations"].append(note)
            block_notes["hospital"].append(note + " — Hospital_*")
            split_block(target, when, entries, classify_hearts_810_key, buckets, stats)
        elif idx == 7:
            block_notes["hearts_0_2"].append(note)
            append_patch(buckets, "hearts_0_2", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 8:
            block_notes["hearts_3_5"].append(note)
            append_patch(buckets, "hearts_3_5", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 9:
            block_notes["gifts"].append(note)
            append_patch(buckets, "gifts", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 10:
            block_notes["gifts"].append(note)
            append_patch(buckets, "gifts", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 11:
            block_notes["dating"].append(note + " — reactions / seasonal")
            block_notes["gifts"].append(note + " — gift keys")
            block_notes["hospital"].append(note + " — Hospital_*")
            block_notes["topics_medical"].append(note + " — topic keys")
            split_block(target, when, entries, classify_dating_key, buckets, stats)
        elif idx == 12:
            block_notes["married"].append(note)
            append_patch(buckets, "married", make_patch(target, entries, when), stats, list(entries.keys()))
        elif 13 <= idx <= 28:
            block_notes["topics_medical"].append(note)
            append_patch(buckets, "topics_medical", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 29:
            block_notes["married"].append(note)
            append_patch(buckets, "married", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 30:
            block_notes["married"].append(note)
            append_patch(buckets, "married", make_patch(target, entries, when), stats, list(entries.keys()))
        elif idx == 31:
            block_notes["base"].append(note)
            append_patch(buckets, "base", make_patch(target, entries, when), stats, list(entries.keys()))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    file_headers = {
        "schedule": "Schedule strings (Harvey)",
        "base": "Base / ungated dialogue (Harvey)",
        "hearts_0_2": "Gifts — Hearts 0–2",
        "hearts_3_5": "Gifts — Hearts 3–5; *4 day lines from block 5",
        "hearts_6_7": "Hearts 4–7 block — *6 day lines only",
        "topics_medical": "Conversation topics (medical / walk / exhaustion / trust)",
        "locations": "Reactions, resort, seasonal, location barks (hearts 4–10)",
        "hospital": "Hospital_* and clinic strict lines",
        "gifts": "AcceptGift / AcceptBirthdayGift (all relationship tiers)",
        "dating": "Relationship:Dating — reactions & seasonal (non-gift)",
        "married": "Married — MarriageDialogue, FarmHouse, storm",
    }

    for fname, bname in LOAD_ORDER:
        patches = buckets.get(bname, [])
        path = OUT_DIR / fname
        write_bucket_file(path, file_headers[bname], patches, block_notes.get(bname, []))
        print(f"{fname}: {len(patches)} patches, {len(stats.get(bname, []))} key slots")

    (ROOT / "docs" / "_split_stats.json").write_text(
        json.dumps({b: stats.get(b, []) for _, b in LOAD_ORDER}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
