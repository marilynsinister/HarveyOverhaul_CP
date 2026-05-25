# -*- coding: utf-8 -*-
"""Patch dialoguesHarvey.json: gift tone layers (preserves // comments)."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "assets/Code/dialoguesHarvey.json"

spec = importlib.util.spec_from_file_location(
    "gift_data", Path(__file__).with_name("gift_tone_layers.py")
)
gift_data = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gift_data)

GIFTS = gift_data.GIFTS
GIFT_KEY_RE = gift_data.GIFT_KEY_RE


def entries_for(tier: str) -> dict:
    return {k: v[tier] for k, v in GIFTS.items()}


def fmt_entries(entries: dict, indent: str = "        ") -> str:
    lines = []
    for k, v in entries.items():
        lines.append(f'{indent}"{k}": {json.dumps(v, ensure_ascii=False)},')
    if lines:
        lines[-1] = lines[-1].rstrip(",")
    return "\n".join(lines)


def make_block(comment: str, when: dict, entries: dict) -> str:
    when_lines = ",\n".join(f'        "{k}": "{v}"' for k, v in when.items())
    return (
        f"    // ===== {comment} =====\n"
        f"    {{\n"
        f'      "Action": "EditData",\n'
        f'      "Target": "Characters/Dialogue/Harvey",\n'
        f'      "Priority": "Late",\n'
        f"      \"When\": {{\n{when_lines}\n"
        f"      }},\n"
        f'      "Entries": {{\n'
        f"{fmt_entries(entries)}\n"
        f"      }}\n"
        f"    }}"
    )


def remove_gift_lines(text: str) -> str:
    out = []
    for line in text.splitlines():
        m = re.search(r'"([^"]+)":\s*', line)
        if m and GIFT_KEY_RE.match(m.group(1)):
            continue
        out.append(line)
    return "\n".join(out)


def find_dating_entries_pos(text: str) -> int:
    dating_when = '"Relationship:Harvey": "Dating"'
    w_idx = text.index(dating_when)
    chunk = text[:w_idx]
    marker = '"Entries": {'
    return chunk.rindex(marker) + len(marker)


def main():
    text = PATH.read_text(encoding="utf-8")
    text = remove_gift_lines(text)

    marker = "    // ===== УРОВЕНЬ 8-10 СЕРДЕЦ (РОМАНТИКА) ===== //"
    idx = text.index(marker)
    blocks = ",\n".join(
        [
            make_block("GIFT REACTIONS — 0-2 СЕРДЦА", {"Hearts:Harvey": "0,1,2"}, entries_for("s0")),
            make_block("GIFT REACTIONS — 3-5 СЕРДЕЦ", {"Hearts:Harvey": "3,4,5"}, entries_for("s1")),
            make_block(
                "GIFT REACTIONS — 6-10 СЕРДЕЦ PRE-DATING",
                {"Hearts:Harvey": "6,7,8,9,10"},
                entries_for("s2"),
            ),
            make_block(
                "GIFT REACTIONS — MARRIED",
                {"Relationship:Harvey": "Married"},
                entries_for("married"),
            ),
        ]
    )
    text = text[:idx] + blocks + ",\n" + text[idx:]

    insert_at = find_dating_entries_pos(text)
    text = text[:insert_at] + "\n" + fmt_entries(entries_for("dating")) + ",\n" + text[insert_at:]

    PATH.write_text(text, encoding="utf-8")
    print(f"Patched {PATH}: {len(GIFTS)} keys x 5 tiers")


if __name__ == "__main__":
    main()
