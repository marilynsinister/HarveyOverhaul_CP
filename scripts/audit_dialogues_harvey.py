#!/usr/bin/env python3
"""Read-only audit of dialoguesHarvey.json — no file modifications."""
import json
import re
from collections import defaultdict
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "assets" / "Code" / "dialoguesHarvey.json"
TARGETS = {
    "Characters/Dialogue/Harvey",
    "Characters/Dialogue/MarriageDialogueHarvey",
    "strings/schedules/Harvey",
}

# Strip // comments (not inside strings — good enough for this file)
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

VY_PATTERN = re.compile(r"\b(Вы|Вас|Вам|Ваш|Ваше|Ваши)\b")
TY_PATTERN = re.compile(
    r"\b(ты|тебя|тебе|твой|твоё|твоя|твоим|твоей|твоих|твоими|доверяешь|помолчи|помни)\b",
    re.IGNORECASE,
)

PROBLEM_PHRASES = [
    ("я не дам", re.compile(r"я не дам", re.I)),
    ("я прослежу", re.compile(r"я прослеж", re.I)),
    ("не спорь", re.compile(r"не спор", re.I)),
    ("не отпущу", re.compile(r"не отпущ", re.I)),
    ("под моим контролем", re.compile(r"под моим контролем|всё под контролем|всё под моим", re.I)),
    ("ты рядом со мной", re.compile(r"ты рядом со мной|рядом со мной", re.I)),
    ("я всегда рядом, даже ночью", re.compile(r"даже ночью|круглосуточно", re.I)),
    ("малышка", re.compile(r"малышк", re.I)),
    ("котёнок", re.compile(r"котёнок|котенок", re.I)),
    ("девочка моя", re.compile(r"девочка моя|моя девочка", re.I)),
    ("открой ротик", re.compile(r"открой рот", re.I)),
    ("кормит с ложки", re.compile(r"кормит.*ложк|с ложки", re.I)),
    ("без возражений", re.compile(r"без возражений|никаких возражений", re.I)),
    ("я сам всё", re.compile(r"я сам всё|я сам прослеж|я сам принес", re.I)),
    ("только моя", re.compile(r"только моя|моё самое дорогое", re.I)),
]

KEY_GROUPS = {
    "Hospital_Mon..Sun": re.compile(r"^Hospital_(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$"),
    "Mon/Tue/.../Sun": re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)$"),
    "Mon2/Tue2...": re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)2$"),
    "Mon4/Tue4...": re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)4$"),
    "Mon6/Tue6...": re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)6$"),
    "Mon8/Tue8...": re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)8$"),
    "Mon10/Tue10...": re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)10$"),
    "GreenRain": re.compile(r"^GreenRain(_2)?$"),
    "timeReaction_*": re.compile(r"^timeReaction_"),
    "locationReaction_*": re.compile(r"^locationReaction_"),
    "emotionalReaction_*": re.compile(r"^emotionalReaction_"),
    "situationReaction_*": re.compile(r"^situationReaction_"),
    "Resort_*": re.compile(r"^Resort"),
    "AcceptGift_*": re.compile(r"^AcceptGift_|^AcceptBirthdayGift_"),
}


def when_label(when: dict | None) -> str:
    if not when:
        return "(нет When)"
    parts = []
    for k, v in when.items():
        parts.append(f"{k}={v}")
    return ", ".join(parts)


def classify_key(key: str) -> list[str]:
    groups = []
    for name, pat in KEY_GROUPS.items():
        if pat.search(key):
            groups.append(name)
    return groups


def main():
    raw = FILE.read_text(encoding="utf-8")
    data = json.loads(strip_comments(raw))
    changes = data.get("Changes", [])

    blocks = []
    block_idx = 0
    for ch in changes:
        if ch.get("Action") != "EditData":
            continue
        target = ch.get("Target")
        if target not in TARGETS:
            continue
        block_idx += 1
        when = ch.get("When")
        entries = ch.get("Entries") or {}
        blocks.append({
            "index": block_idx,
            "target": target,
            "when": when,
            "when_label": when_label(when),
            "priority": ch.get("Priority"),
            "entry_count": len(entries),
            "keys": list(entries.keys()),
            "entries": entries,
        })

    # Key -> list of block indices
    key_blocks: dict[str, list[int]] = defaultdict(list)
    for b in blocks:
        for k in b["keys"]:
            key_blocks[k].append(b["index"])

    duplicates = {k: idxs for k, idxs in key_blocks.items() if len(idxs) > 1}

    # Group duplicates by key pattern
    pattern_dupes: dict[str, dict[str, list[int]]] = defaultdict(dict)
    for k, idxs in duplicates.items():
        for g in classify_key(k):
            pattern_dupes[g][k] = idxs
        if not classify_key(k):
            pattern_dupes["other"][k] = idxs

    mixed_vy_ty = []
    problems = defaultdict(list)

    for b in blocks:
        for key, text in b["entries"].items():
            has_vy = bool(VY_PATTERN.search(text))
            has_ty = bool(TY_PATTERN.search(text))
            if has_vy and has_ty:
                mixed_vy_ty.append({
                    "block": b["index"],
                    "target": b["target"],
                    "when": b["when_label"],
                    "key": key,
                    "preview": text[:120].replace("\n", " ") + ("…" if len(text) > 120 else ""),
                })
            for pname, pat in PROBLEM_PHRASES:
                if pat.search(text):
                    problems[pname].append({
                        "block": b["index"],
                        "when": b["when_label"],
                        "key": key,
                        "target": b["target"],
                    })

    # Output summary for report generation
    print("=== BLOCKS ===")
    for b in blocks:
        print(f"#{b['index']} | {b['target']} | When: {b['when_label']} | Entries: {b['entry_count']}")

    print("\n=== DUPLICATE KEY COUNT ===", len(duplicates))
    print("\n=== PATTERN DUPLICATES ===")
    for g in sorted(pattern_dupes.keys()):
        keys = pattern_dupes[g]
        if keys:
            print(f"{g}: {len(keys)} keys in multiple blocks")

    print("\n=== MIXED VY/TY ===", len(mixed_vy_ty))
    for m in mixed_vy_ty[:5]:
        print(m)

    print("\n=== PROBLEM PHRASE COUNTS ===")
    for pname, items in sorted(problems.items(), key=lambda x: -len(x[1])):
        print(f"{pname}: {len(items)}")

    # Write JSON for report helper
    out = Path(__file__).resolve().parents[1] / "docs" / "_audit_dialogues_harvey_data.json"
    import json as j
    out.write_text(j.dumps({
        "blocks": [{k: v for k, v in b.items() if k != "entries"} for b in blocks],
        "duplicates_count": len(duplicates),
        "duplicates": {k: v for k, v in sorted(duplicates.items()) if any(classify_key(k)) or True},
        "pattern_dupes": {g: list(keys.keys()) for g, keys in pattern_dupes.items()},
        "mixed_vy_ty": mixed_vy_ty,
        "problems": {k: v for k, v in problems.items()},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
