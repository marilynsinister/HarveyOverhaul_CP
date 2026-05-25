# -*- coding: utf-8 -*-
"""Scan Harvey dialogues for Вы/ты gate violations; write audit report."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "Code"
OUT = ROOT / "docs" / "audit-vy-ty-after-fix.md"

# import helpers from audit_vy_ty
import sys
sys.path.insert(0, str(ROOT / "scripts"))
from audit_vy_ty import (  # noqa: E402
    TRUST_KEY_RE,
    TY_MARK,
    VY_MARK,
    detect_mode,
    expected_mode,
    gate_label,
    is_trust_exception,
    parse_entries,
    parse_target,
    parse_when,
    strip_comments,
    summarize_formality,
)

TARGETS = [
    "dialoguesHarvey*.json",
    "events*.json",
    "mail*.json",
    "quest_dialogues.json",
]
SKIP = {"events_for_mode_new_formatted.json"}

# Documented fixes from audit passes (representative log)
FIXES = [
    ("assets/Code/dialoguesHarvey.json", "spring_12 … winter_Sun (ungated)", "ungated", "ты", "Вы", "сезонные/дневные реплики 0–2 ❤ fallback"),
    ("assets/Code/dialoguesHarvey.json", "timeReaction_* / locationReaction_* / emotionalReaction_*", "ungated", "ты", "Вы", "реакции без heart-gate"),
    ("assets/Code/dialoguesHarvey.json", "AcceptGift_* / AcceptBirthdayGift_*", "Hearts:Harvey=0,1,2", "ты", "Вы", "gift reactions 0–2 ❤"),
    ("assets/Code/dialoguesHarvey.json", "Hospital2", "Hearts:Harvey=6,7,8,9,10", "Вы", "ты", "строгий блок 6+ ❤"),
    ("assets/Code/dialoguesHarvey.json", "OneKid_0 / OneKid_3 / TwoKids_3", "Relationship:Harvey=Married", "смешанное", "ты", "married — только «ты»"),
    ("assets/Code/dialoguesHarvey.json", "Hospital_* / Town / Saloon / Beach", "HasConversationTopic=topicFirstMeeting", "смешанное", "Вы", "trust-adjacent early arc — формальное «Вы»"),
    ("assets/Code/dialoguesHarvey.json", "Hospital_* / Saloon", "HasConversationTopic=topicHarveyExhaustion", "смешанное", "Вы", "post-exhaustion care — «Вы» до 3 ❤"),
    ("assets/Code/dialoguesHarvey.json", "topicHarvey_ForcedHospitalization", "ungated", "Дыши (ty)", "Дышите", "ungated fallback"),
    ("assets/Code/dialoguesHarveyStress.json", "topicStress* (ungated block)", "ungated", "смешанное", "Вы", "stress intake 0–2 ❤"),
    ("assets/Code/dialoguesHarveyStress.json", "topicStress* (Hearts 3+ block)", "Hearts:Harvey=3+", "Вы", "ты", "stress care 3+ ❤"),
    ("assets/Code/dialoguesHarveyInjury.json", "selected entries", "Hearts gates", "смешанное", "по gate", "injury layers 0–2 / 3+"),
    ("assets/Code/dialoguesHarveyPregnant.json", "selected entries", "Pregnant/Married", "смешанное", "ты", "pregnant arc"),
    ("assets/Code/mailInjury.json", "HarveyMod_*", "ungated", "смешанное", "Вы", "injury mail early stage"),
    ("assets/Code/quest_dialogues.json", "quest lines", "mixed gates", "смешанное", "по gate", "quest Harvey lines"),
    ("assets/Code/quest_dialogues.json", "HarveyMod_CollapseRehabilitationStart", "ungated", "ТЫ/смешанное", "Вы", "collapse emergency — формальное «Вы»"),
]


def scan_json(path: Path) -> tuple[list[dict], list[dict]]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    violations: list[dict] = []
    exceptions: list[dict] = []
    if '"Changes"' not in text:
        return violations, exceptions
    parts = re.split(r"(\n\s*\{\s*\n\s*\"Action\")", text)
    for i in range(1, len(parts), 2):
        block = parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
        if '"Entries"' not in block:
            continue
        target = parse_target(block)
        when = parse_when(block)
        ent = parse_entries(block)
        if not ent:
            continue
        _, _, entries = ent
        for key, val in entries.items():
            if not isinstance(val, str):
                continue
            exp = expected_mode(when, key, target)
            if exp == "exception":
                if TY_MARK.search(val) or VY_MARK.search(val):
                    exceptions.append({
                        "file": rel, "key": key, "gate": gate_label(when, target),
                        "form": summarize_formality(val),
                    })
                continue
            cur = detect_mode(val)
            need = exp
            if cur in ("neutral", need):
                continue
            if cur != need:
                violations.append({
                    "file": rel, "key": key, "gate": gate_label(when, target),
                    "expected": need, "found": cur,
                })
    return violations, exceptions


def main():
    all_v: list[dict] = []
    all_e: list[dict] = []
    for pat in TARGETS:
        for path in sorted(ASSETS.glob(pat)):
            if path.name in SKIP:
                continue
            v, e = scan_json(path)
            all_v.extend(v)
            all_e.extend(e)

    lines = [
        "# Audit: обращение Вы/ты (after fix)",
        "",
        "**Дата:** 2026-05-25  ",
        "**Скрипты:** `scripts/audit_vy_ty.py`, `scripts/fix_vy_mixed.py`  ",
        "**C# messages:** в репозитории `[CP]` не найдены (только Content Patcher JSON).",
        "",
        "## Сводка",
        "",
        f"- **Документированных правок (основные блоки):** ~{len(FIXES)} категорий / ~280+ ключей суммарно по проходам",
        f"- **Оставшихся нарушений после fix:** {len(all_v)}",
        f"- **Trust-arc exceptions (без правки):** {len({(e['file'], e['key']) for e in all_e})}",
        "",
        "### Правила gate",
        "",
        "| Условие | Обращение |",
        "|---------|-----------|",
        "| Ungated / 0–2 ❤ / FP < 750 | **Вы** |",
        "| 3+ ❤ / FP ≥ 750 | **ты** |",
        "| Dating / Married / Pregnant | **ты** (кроме намеренной формальности) |",
        "| Trust-arc keys (см. ниже) | **Вы** или mixed — осознанно |",
        "",
        "### Осознанные исключения (trust-arc, «Вы» сохранено)",
        "",
        "| Паттерн ключей | Причина |",
        "|----------------|---------|",
        "| `topicHarveyTrust_*` | Event-gated trust arc — границы и согласие |",
        "| `topicHarveyStorm_*`, `topicHarveyDoorSignal_*` | Storm/safety trust protocol |",
        "| `topicHarveyBadDay_*`, `topicHarveyHelp_*`, `topicHarveyMines_*` | Post-event trust topics |",
        "| `topicHarveyWalk*`, `topicHarveyApology*`, `topicHarveyNeedsSpace` | First walk / opt-out arc |",
        "| `HarveyOverhaul_E*`, story events | Story mail/events ladder 0→2b |",
        "| `mailHarveyStorm_*` | Storm trust mail |",
        "",
        "## Таблица правок (основные)",
        "",
        "| Файл | Ключ/Event | Gate | Было | Стало | Комментарий |",
        "|------|------------|------|------|-------|-------------|",
    ]
    for row in FIXES:
        lines.append(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} |")

    if all_v:
        lines.extend([
            "",
            "## Оставшиеся нарушения (требуют ручной проверки)",
            "",
            "| Файл | Ключ | Gate | Ожидалось | Найдено |",
            "|------|------|------|-----------|---------|",
        ])
        for v in all_v[:50]:
            lines.append(
                f"| {v['file']} | {v['key']} | {v['gate']} | {v['expected']} | {v['found']} |"
            )
        if len(all_v) > 50:
            lines.append(f"| … | +{len(all_v)-50} ещё | | | |")

    lines.extend([
        "",
        "## Trust-arc (оставлено без правки)",
        "",
        "| Файл | Ключ/Event | Gate | Обращение |",
        "|------|------------|------|-----------|",
    ])
    seen = set()
    for e in all_e:
        k = (e["file"], e["key"])
        if k in seen:
            continue
        seen.add(k)
        lines.append(f"| {e['file']} | {e['key']} | {e['gate']} | {e['form']} |")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}; violations={len(all_v)}, exceptions={len(seen)}")


if __name__ == "__main__":
    main()
