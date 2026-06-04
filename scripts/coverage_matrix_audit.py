#!/usr/bin/env python3
"""Coverage matrix audit for Harvey split dialogues → docs/dialogues_harvey_coverage_matrix.md"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUES_DIR = ROOT / "assets" / "Code" / "dialogues"
REPORT = ROOT / "docs" / "dialogues_harvey_coverage_matrix.md"

LOAD_ORDER = [
    "harvey_schedule_strings.json",
    "harvey_base.json",
    "harvey_hearts_0_2.json",
    "harvey_hearts_3_5.json",
    "harvey_hearts_6_7.json",
    "harvey_topics_medical.json",
    "harvey_locations.json",
    "harvey_hospital.json",
    "harvey_gifts.json",
    "harvey_dating.json",
    "harvey_married.json",
    "harvey_priority2.json",
]

TARGET_DIALOGUE = "Characters/Dialogue/Harvey"
TARGET_MARRIAGE = "Characters/Dialogue/MarriageDialogueHarvey"

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
SUFFIXES = ("", "2", "4", "6", "8", "10")

TIERS = (
    "base",
    "hearts_0_2",
    "hearts_3_5",
    "hearts_6_7",
    "hearts_8_10",
    "dating",
    "married",
)

TIER_LABELS = {
    "base": "Base",
    "hearts_0_2": "0–2 ❤",
    "hearts_3_5": "3–5 ❤",
    "hearts_6_7": "6–7 ❤",
    "hearts_8_10": "8–10 ❤",
    "dating": "Dating",
    "married": "Married",
}


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


def parse_json(path: Path) -> dict:
    return json.loads(strip_comments(path.read_text(encoding="utf-8")))


def hearts_set(when: dict | None) -> set[int] | None:
    if not when:
        return None
    h = when.get("Hearts:Harvey")
    if not h:
        return None
    return {int(x.strip()) for x in str(h).split(",")}


def relationship(when: dict | None) -> str | None:
    if not when:
        return None
    return when.get("Relationship:Harvey")


def has_topic_when(when: dict | None) -> bool:
    if not when:
        return False
    return any(k.startswith("HasConversationTopic") for k in when)


@dataclass
class Patch:
    order: int
    file: str
    target: str
    when: dict | None
    entries: dict[str, str]

    def when_label(self) -> str:
        if not self.when:
            return "(нет When)"
        return ", ".join(f"{k}={v}" for k, v in self.when.items())


def patch_tiers(p: Patch) -> set[str]:
    tiers: set[str] = set()
    if p.target == TARGET_MARRIAGE:
        tiers.add("married")
        return tiers
    if p.target != TARGET_DIALOGUE:
        return tiers

    rel = relationship(p.when)
    hs = hearts_set(p.when)

    if p.when is None:
        tiers.add("base")
        return tiers

    if has_topic_when(p.when):
        # topic overlay — attribute heart/relationship slices only
        if rel == "Dating":
            tiers.add("dating")
        elif rel == "Married":
            tiers.add("married")
        if hs:
            if hs <= {0, 1, 2}:
                tiers.add("hearts_0_2")
            elif hs <= {3, 4, 5}:
                tiers.add("hearts_3_5")
            else:
                if hs & {6, 7}:
                    tiers.add("hearts_6_7")
                if hs & {8, 9, 10}:
                    tiers.add("hearts_8_10")
        return tiers

    if rel == "Dating":
        tiers.add("dating")
        return tiers
    if rel == "Married":
        tiers.add("married")
        return tiers

    if hs is not None:
        if hs <= {0, 1, 2}:
            tiers.add("hearts_0_2")
        if hs & {3, 4, 5}:
            tiers.add("hearts_3_5")
        if hs & {6, 7}:
            tiers.add("hearts_6_7")
        if hs & {8, 9, 10}:
            tiers.add("hearts_8_10")
        return tiers

    # When without hearts/relationship (e.g. Weather) — treat as married-only if married file
    if "married" in p.file:
        tiers.add("married")
    elif "dating" in p.file:
        tiers.add("dating")
    else:
        tiers.add("base")
    return tiers


def load_patches() -> list[Patch]:
    patches: list[Patch] = []
    order = 0
    for fname in LOAD_ORDER:
        path = DIALOGUES_DIR / fname
        data = parse_json(path)
        for ch in data.get("Changes", []):
            if ch.get("Action") != "EditData":
                continue
            target = ch.get("Target")
            if target not in (TARGET_DIALOGUE, TARGET_MARRIAGE):
                continue
            order += 1
            patches.append(
                Patch(
                    order=order,
                    file=fname,
                    target=target,
                    when=ch.get("When"),
                    entries=ch.get("Entries") or {},
                )
            )
    return patches


# --- canonical key sets ---
def weekday_keys() -> list[str]:
    keys = []
    for suf in SUFFIXES:
        for d in DAYS:
            keys.append(f"{d}{suf}")
    return keys


def hospital_keys() -> list[str]:
    keys = [f"Hospital_{d}" for d in DAYS]
    keys += ["Hospital", "Hospital2", "Hospital4", "Hospital6", "Hospital8", "Hospital10", "Hospital_Entry"]
    return keys


def time_situation_keys() -> list[str]:
    return [
        "timeReaction_Late",
        "timeReaction_VeryLate",
        "timeReaction_Early",
        "situationReaction_Exhausted",
        "situationReaction_Injured",
        "situationReaction_Drunk",
        "emotionalReaction_Crying",
        "emotionalReaction_Scared",
    ]


def location_prefixes() -> list[str]:
    return [
        "locationReaction_Mine",
        "locationReaction_SkullCave",
        "Desert",
        "Beach",
        "Resort",
        "HarveyRoom",
        "ArchaeologyHouse",
    ]


def season_festival_pattern() -> re.Pattern:
    return re.compile(r"^(spring|summer|fall|winter)_", re.I)


def medical_topic_pattern() -> re.Pattern:
    return re.compile(
        r"^(topicHarvey_|topicHarveyTrust_|topicHarveyStorm_|topicHarveyBadDay_)"
        r"|topicHarvey.*(Injur|Treat|Hospital|Mines|Exhaust|Stress|Wet|Bandage|Forced)"
        r"|Treat_|Support_|PhaseTransition_|Recovery_Complete_",
        re.I,
    )


def key_matches_location(key: str, prefix: str) -> bool:
    if prefix.startswith("locationReaction_"):
        return key == prefix or key.startswith(prefix)
    return key == prefix or key.startswith(prefix)


def collect_all_keys(patches: list[Patch]) -> dict[str, set[str]]:
    """key -> tiers"""
    coverage: dict[str, set[str]] = defaultdict(set)
    key_sources: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for p in patches:
        tiers = patch_tiers(p)
        for k in p.entries:
            coverage[k].update(tiers)
            key_sources[k].append((p.file, p.when_label()))

    return coverage, key_sources


def matrix_row(key: str, cov: set[str]) -> str:
    cells = []
    for t in TIERS:
        mark = "✓" if t in cov else "—"
        cells.append(mark)
    return f"| `{key}` | " + " | ".join(cells) + " |"


def matrix_header() -> str:
    hdr = "| Ключ | " + " | ".join(TIER_LABELS[t] for t in TIERS) + " |"
    sep = "|------|" + "|".join(["---"] * len(TIERS)) + "|"
    return hdr + "\n" + sep


def keys_in_group(coverage: dict[str, set[str]], keys: list[str]) -> list[str]:
    return [k for k in keys if k in coverage]


def keys_matching(coverage: dict[str, set[str]], pred) -> list[str]:
    return sorted(k for k in coverage if pred(k))


def when_overlap(a: dict | None, b: dict | None) -> bool:
    if a is None or b is None:
        return True
    ra, rb = relationship(a), relationship(b)
    if ra and rb and ra != rb:
        return False
    ha, hb = hearts_set(a), hearts_set(b)
    if ha and hb and not (ha & hb):
        return False
    ta = frozenset(k for k in (a or {}) if k.startswith("HasConversationTopic"))
    tb = frozenset(k for k in (b or {}) if k.startswith("HasConversationTopic"))
    if ta and tb and ta != tb:
        return False
    if (ta or tb) and ta != tb:
        pass
    shared = set(a) & set(b) - {"Hearts:Harvey", "Relationship:Harvey"}
    for k in shared:
        if a[k] != b[k]:
            return False
    return True


def specificity_score(when: dict | None) -> int:
    if not when:
        return 0
    score = len(when) * 10
    if relationship(when):
        score += 50
    if hearts_set(when):
        score += 20
    if any(k.startswith("HasConversationTopic") for k in when):
        score += 40
    return score


def gap_list(
    coverage: dict[str, set[str]],
    keys: list[str],
    need: set[str],
    *,
    also_have: set[str] | None = None,
) -> list[str]:
    out = []
    for k in keys:
        cov = coverage.get(k, set())
        if also_have and not (also_have & cov):
            continue
        if need - cov:
            missing = ", ".join(TIER_LABELS[t] for t in TIERS if t in (need - cov))
            have = ", ".join(TIER_LABELS[t] for t in TIERS if t in cov) or "—"
            out.append(f"`{k}` — есть: {have}; нет: {missing}")
    return out


def main() -> None:
    patches = load_patches()
    coverage, key_sources = collect_all_keys(patches)

    # Build key -> list of patches for overlap analysis
    key_patches: dict[str, list[Patch]] = defaultdict(list)
    for p in patches:
        for k in p.entries:
            key_patches[k].append(p)

    overlapping_winners: list[str] = []
    for key, ps in sorted(key_patches.items()):
        if len(ps) < 2:
            continue
        overlap_pairs = []
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if when_overlap(ps[i].when, ps[j].when):
                    overlap_pairs.append((ps[i], ps[j]))
        if not overlap_pairs:
            continue
        # winner = last in load order
        winner = max(ps, key=lambda x: x.order)
        ambiguous = []
        for a, b in overlap_pairs:
            if a.order != b.order and when_overlap(a.when, b.when):
                if specificity_score(a.when) > specificity_score(b.when) and a.order < b.order:
                    ambiguous.append(
                        f"`{key}`: более специфичный ({a.file}, {a.when_label()}) "
                        f"раньше общего ({b.file}, {b.when_label()}) — риск перебивания base/generic"
                    )
                elif specificity_score(b.when) > specificity_score(a.when) and b.order < a.order:
                    ambiguous.append(
                        f"`{key}`: более специфичный ({b.file}, {b.when_label()}) "
                        f"раньше общего ({a.file}, {a.when_label()})"
                    )
        if len(ps) >= 2 and any(when_overlap(x.when, y.when) for x in ps for y in ps if x != y):
            others = [p for p in ps if p.order != winner.order and when_overlap(p.when, winner.when)]
            if others and key not in {x.split("`")[1] for x in overlapping_winners}:
                labels = "; ".join(
                    f"#{p.order} {p.file} ({p.when_label()})" for p in sorted(ps, key=lambda x: x.order)
                )
                overlapping_winners.append(
                    f"`{key}` — {len(ps)} патчей, побеждает #{winner.order} {winner.file}: {labels}"
                )

    # Dedupe ambiguous messages
    seen_amb = set()
    order_risk: list[str] = []
    for key, ps in sorted(key_patches.items()):
        if len(ps) < 2:
            continue
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if not when_overlap(ps[i].when, ps[j].when):
                    continue
                if specificity_score(ps[i].when) > specificity_score(ps[j].when) and ps[i].order < ps[j].order:
                    msg = (
                        f"`{key}`: #{ps[i].order} {ps[i].file} ({ps[i].when_label()}) "
                        f"перебивается #{ps[j].order} {ps[j].file} ({ps[j].when_label()})"
                    )
                    if msg not in seen_amb:
                        seen_amb.add(msg)
                        order_risk.append(msg)

    all_keys = set(coverage.keys())

    # Gap categories (dialogue keys only, exclude pure gifts unless in group)
    def dialogue_keys() -> set[str]:
        return {k for k in all_keys if not k.startswith("AcceptGift_") and not k.startswith("AcceptBirthdayGift_")}

    dk = dialogue_keys()

    base_no_dating = sorted(k for k in dk if "base" in coverage[k] and "dating" not in coverage[k])
    base_no_married = sorted(k for k in dk if "base" in coverage[k] and "married" not in coverage[k])
    mid_no_high = sorted(
        k
        for k in dk
        if ("hearts_6_7" in coverage[k] or "hearts_3_5" in coverage[k])
        and "hearts_8_10" not in coverage[k]
        and "dating" not in coverage[k]
    )
    topics_unsplit = sorted(
        k
        for k in dk
        if k.startswith("topicHarvey")
        and len(coverage[k]) <= 1
        and "base" in coverage[k]
    )
    topics_any = sorted(k for k in dk if k.startswith("topicHarvey"))
    topics_by_tier_count = defaultdict(list)
    for k in topics_any:
        tc = len(coverage[k] & {"base", "hearts_0_2", "hearts_3_5", "hearts_6_7", "hearts_8_10", "dating", "married"})
        topics_by_tier_count[tc].append(k)

    dating_no_married = sorted(k for k in dk if "dating" in coverage[k] and "married" not in coverage[k])
    married_no_dating = sorted(
        k for k in dk if "married" in coverage[k] and "dating" not in coverage[k]
    )

    med_keys_all = keys_matching(coverage, lambda k: bool(medical_topic_pattern().search(k)))
    only_base = [k for k in med_keys_all if coverage[k] == {"base"}]

    # Priority gaps for writing
    priority: list[tuple[int, str, str]] = []

    def add_priority(score: int, key: str, reason: str):
        priority.append((score, key, reason))

    for k in weekday_keys() + hospital_keys() + time_situation_keys():
        if k not in coverage:
            add_priority(10, k, "ключ отсутствует полностью")
            continue
        cov = coverage[k]
        if "base" in cov and "dating" not in cov:
            add_priority(8, k, "есть Base, нет Dating — при романе уйдёт в базу")
        if "base" in cov and "married" not in cov:
            add_priority(7, k, "есть Base, нет Married")
        if ("hearts_6_7" in cov or "hearts_3_5" in cov) and "hearts_8_10" not in cov and "dating" not in cov:
            add_priority(6, k, "есть 3–7 ❤, нет 8–10 и Dating")

    for k in topics_unsplit[:80]:
        add_priority(9, k, "topic только в Base — без стадий отношений")

    priority.sort(key=lambda x: (-x[0], x[1]))

    lines: list[str] = []
    lines.append("# Матрица покрытия диалогов Харви по уровням отношений")
    lines.append("")
    lines.append("**Дата:** 2026-06-04  ")
    lines.append("**Источник:** split-файлы `assets/Code/dialogues/harvey_*.json` (manifest `dialoguesHarvey.json`)  ")
    lines.append("**Режим:** аудит покрытия; приоритет 1–2 дополнены в split-файлах (см. §9–10).")
    lines.append("")
    lines.append("## Легенда")
    lines.append("")
    lines.append("| Символ | Значение |")
    lines.append("|--------|----------|")
    lines.append("| ✓ | Есть хотя бы один патч `EditData` с этим ключом и условием стадии |")
    lines.append("| — | Нет отдельного варианта для стадии |")
    lines.append("")
    lines.append(
        "**Стадии:** Base = блок без `When`; сердечные — по `Hearts:Harvey`; Dating/Married — по `Relationship:Harvey`. "
        "Topic-патчи с `HasConversationTopic` учитываются только в своих стадиях (не размазываются на Base)."
    )
    lines.append("")
    lines.append(
        f"**Охват:** {len(patches)} патчей, {len(all_keys)} уникальных ключей в `Characters/Dialogue/Harvey` + MarriageDialogue."
    )
    lines.append("")
    lines.append("## Краткие выводы")
    lines.append("")
    lines.append("| Метрика | Значение |")
    lines.append("|---------|----------|")
    lines.append(f"| Ключей: Base без Dating | {len(base_no_dating)} |")
    lines.append(f"| Ключей: Base без Married | {len(base_no_married)} |")
    lines.append(f"| Ключей: 3–7 ❤ без 8–10 и Dating | {len(mid_no_high)} |")
    lines.append(f"| topicHarvey* только в Base | {len(only_base)} |")
    lines.append(f"| Dating без Married | {len(dating_no_married)} |")
    lines.append(f"| Married без Dating | {len(married_no_dating)} |")
    lines.append(f"| Ключей с пересекающимися When | {len(overlapping_winners)} |")
    lines.append(f"| ⚠️ Специфичный патч раньше общего | {len(order_risk)} |")
    lines.append("")
    lines.append(
        "**Главный риск:** базовый слой (`harvey_base.json`) и блоки 4–7 ❤ без отдельных Dating/Married — "
        "при романе/браке игра часто возьмёт формальный «Вы» или нейтральный тон из Base."
    )
    lines.append("")
    lines.append(
        "**Лестница дней недели:** `Mon`–`Sun` / `*2` — только Base (+ частично Married для `Mon`/`Tue`/`Sat`); "
        "`*4`/`*6` — 3–7 ❤; `*8`/`*10` — 8–10 + Dating, без Married."
    )
    lines.append("")
    lines.append(
        "**Topic-травмы:** ~35 ключей `topicHarvey_*` в Base без разбивки по сердцам; "
        "исключения с Dating: `topicHarveyBadDay_*`, `topicHarveyMines_*`, часть `topicHarveyTrust_*`."
    )
    lines.append("")

    # §1 Weekdays
    lines.append("## 1. Повседневные (дни недели)")
    lines.append("")
    for title, suf in [
        ("Mon–Sun", ""),
        ("Mon2–Sun2", "2"),
        ("Mon4–Sun4", "4"),
        ("Mon6–Sun6", "6"),
        ("Mon8–Sun8", "8"),
        ("Mon10–Sun10", "10"),
    ]:
        keys = [f"{d}{suf}" for d in DAYS]
        present = keys_in_group(coverage, keys)
        lines.append(f"### {title}")
        lines.append("")
        if not present:
            lines.append("*Нет ключей в данных.*")
        else:
            lines.append(matrix_header())
            for k in keys:
                if k in coverage:
                    lines.append(matrix_row(k, coverage[k]))
        lines.append("")

    # §2 Hospital
    lines.append("## 2. Госпиталь")
    lines.append("")
    lines.append(matrix_header())
    for k in hospital_keys():
        if k in coverage:
            lines.append(matrix_row(k, coverage[k]))
        else:
            lines.append(f"| `{k}` | " + " | ".join(["—"] * len(TIERS)) + " |")
    lines.append("")

    # §3 Time/state
    lines.append("## 3. Время и состояние")
    lines.append("")
    lines.append(matrix_header())
    for k in time_situation_keys():
        lines.append(matrix_row(k, coverage.get(k, set())))
    lines.append("")

    # §4 Locations
    lines.append("## 4. Локации")
    lines.append("")
    loc_keys: dict[str, list[str]] = {}
    for prefix in location_prefixes():
        loc_keys[prefix] = sorted(
            k for k in coverage if key_matches_location(k, prefix)
        )
    for prefix, keys in loc_keys.items():
        lines.append(f"### `{prefix}*`")
        lines.append("")
        if not keys:
            lines.append("*Ключей не найдено.*")
        else:
            lines.append(matrix_header())
            for k in keys:
                lines.append(matrix_row(k, coverage[k]))
        lines.append("")

    # §5 Seasonal
    lines.append("## 5. Сезонные и фестивальные (`spring_*`, `summer_*`, `fall_*`, `winter_*`)")
    lines.append("")
    season_keys = keys_matching(coverage, lambda k: bool(season_festival_pattern().match(k)))
    by_season: dict[str, list[str]] = defaultdict(list)
    for k in season_keys:
        by_season[k.split("_")[0].lower()].append(k)
    for season in ("spring", "summer", "fall", "winter"):
        keys = sorted(by_season.get(season, []))
        lines.append(f"### {season}_* ({len(keys)} ключей)")
        lines.append("")
        if len(keys) > 40:
            # summary table: tier coverage counts
            lines.append("| Стадия | Ключей с покрытием |")
            lines.append("|--------|-------------------|")
            for t in TIERS:
                n = sum(1 for k in keys if t in coverage[k])
                lines.append(f"| {TIER_LABELS[t]} | {n} |")
            lines.append("")
            lines.append("<details><summary>Полная матрица</summary>")
            lines.append("")
            lines.append(matrix_header())
            for k in keys:
                lines.append(matrix_row(k, coverage[k]))
            lines.append("")
            lines.append("</details>")
        elif keys:
            lines.append(matrix_header())
            for k in keys:
                lines.append(matrix_row(k, coverage[k]))
        else:
            lines.append("*Нет ключей.*")
        lines.append("")

    # §6 Medical topics
    lines.append("## 6. Медицинские topic и связанные ключи")
    lines.append("")
    med_keys = med_keys_all
    lines.append(f"Всего ключей в группе: **{len(med_keys)}**.")
    lines.append("")
    lines.append(f"- Только Base (без стадий): **{len(only_base)}**")
    lines.append(f"- С 2+ стадиями: **{sum(1 for k in med_keys if len(coverage[k]) >= 2)}**")
    lines.append("")
    lines.append("### Префиксы")
    lines.append("")
    prefixes = [
        ("topicHarvey_", lambda k: k.startswith("topicHarvey_")),
        ("topicHarveyTrust_", lambda k: k.startswith("topicHarveyTrust_")),
        ("topicHarveyStorm_", lambda k: k.startswith("topicHarveyStorm_")),
        ("topicHarveyBadDay_", lambda k: k.startswith("topicHarveyBadDay_")),
        ("прочие topicHarvey*", lambda k: k.startswith("topicHarvey") and not k.startswith("topicHarvey_")),
    ]
    for label, pred in prefixes:
        sub = sorted(k for k in med_keys if pred(k))
        lines.append(f"- **{label}**: {len(sub)}")
    lines.append("")
    lines.append("<details><summary>Матрица topicHarvey_* (только Base)</summary>")
    lines.append("")
    lines.append(matrix_header())
    for k in only_base[:60]:
        lines.append(matrix_row(k, coverage[k]))
    if len(only_base) > 60:
        lines.append(f"\n*… и ещё {len(only_base) - 60} ключей*")
    lines.append("")
    lines.append("</details>")
    lines.append("")
    lines.append("<details><summary>Матрица topic с разделением по стадиям</summary>")
    lines.append("")
    multi = [k for k in med_keys if len(coverage[k]) >= 2]
    lines.append(matrix_header())
    for k in sorted(multi):
        lines.append(matrix_row(k, coverage[k]))
    lines.append("")
    lines.append("</details>")
    lines.append("")

    # §7 Gap lists
    lines.append("---")
    lines.append("")
    lines.append("## 7. Пробелы и риски (сводные списки)")
    lines.append("")

    def section(title: str, items: list[str], limit: int = 120):
        lines.append(f"### {title}")
        lines.append("")
        lines.append(f"**Всего:** {len(items)}")
        lines.append("")
        for item in items[:limit]:
            lines.append(f"- {item}")
        if len(items) > limit:
            lines.append(f"- *… и ещё {len(items) - limit}*")
        lines.append("")

    section("1. Есть Base, нет Dating", base_no_dating)
    section("2. Есть Base, нет Married", base_no_married)
    section("3. Есть 3–7 ❤, нет 8–10 и Dating", mid_no_high)
    section("4. Topic-ключи только в Base (без стадий)", topics_unsplit)
    section("5. Есть Dating, нет Married", dating_no_married)
    section("6. Есть Married, нет Dating", married_no_dating)

    lines.append("### 7. Пересекающиеся When (неясный победитель)")
    lines.append("")
    lines.append(
        "При `Priority: Late` побеждает **последний** патч в порядке manifest. "
        "Ниже — ключи с 2+ патчами и пересекающимися условиями; ⚠️ — более специфичный патч идёт **раньше** общего."
    )
    lines.append("")
    lines.append(f"**Ключей с пересечением:** {len(overlapping_winners)}")
    lines.append("")
    for item in overlapping_winners[:80]:
        lines.append(f"- {item}")
    if len(overlapping_winners) > 80:
        lines.append(f"- *… и ещё {len(overlapping_winners) - 80}*")
    lines.append("")
    lines.append("**⚠️ Риск порядка (специфичный раньше общего):**")
    lines.append("")
    for item in order_risk[:50]:
        lines.append(f"- {item}")
    if len(order_risk) > 50:
        lines.append(f"- *… и ещё {len(order_risk) - 50}*")
    lines.append("")

    # §8 Priority recommendations
    lines.append("## 8. Приоритет дописывания (рекомендация)")
    lines.append("")
    lines.append("Порядок — по влиянию на «не тот тон» при смене отношений:")
    lines.append("")
    seen_p = set()
    n = 0
    for score, key, reason in priority:
        if key in seen_p:
            continue
        seen_p.add(key)
        n += 1
        lines.append(f"{n}. **{key}** — {reason}")
        if n >= 35:
            break
    lines.append("")
    lines.append("### Групповые приоритеты")
    lines.append("")
    lines.append("| Группа | Рекомендация |")
    lines.append("|--------|----------------|")
    lines.append(
        "| Повседневные Mon–Sun10 | Для каждого суффикса закрыть Dating и Married, если сейчас только Base + heart-блоки |"
    )
    lines.append(
        "| Hospital_* | `Hospital_Mon`–`Sun` и `Hospital8`/`10` — проверить Dating; married частично в `harvey_married` |"
    )
    lines.append(
        "| time/situation/emotional | Все 8 ключей дублируются в base + hearts_4_7 + 8_10 + dating; убедиться, что married-варианты осмысленны |"
    )
    lines.append(
        "| Локации Desert/Beach/Resort | Base перебивает topic-overlays при неверном порядке — дописать/переставить не нужно в этом шаге; дописать Married для Resort* |"
    )
    lines.append(
        f"| topicHarvey_* только Base | **{len(only_base)}** ключей — главный долг: разнести по 0–2 / 3–10 / Dating / Married |"
    )
    lines.append(
        "| Treat_* / Injury (в `dialoguesHarveyCure` / `Injury`) | Вне этого manifest; стадии Stranger/Dating/Married — отдельный проход |"
    )
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 9. Приоритет 2 — закрыто (2026-06-04)")
    lines.append("")
    lines.append("Файл: `assets/Code/dialogues/harvey_priority2.json` (после `harvey_married` в manifest).")
    lines.append("")
    lines.append("| Группа | Добавлено |")
    lines.append("|--------|-----------|")
    lines.append("| Повседневные `Mon`–`Sun`, `Mon2`–`Sun2` | Dating (14) — base с «Вы»; Married (14) — клиника/NPC |")
    lines.append("| `Mon8`–`Sun8`, `Mon10`–`Sun10` | Married (14) |")
    lines.append("| Локации | Dating: `Desert`, `Desert2`, `Beach2`, `HarveyRoom`, `HarveyRoom2`; Married: +8/10, Archaeology*, Resort |")
    lines.append("| Сезонные `spring_Mon`…`winter_Sun` | Married (28) |")
    lines.append("| Фестивали | Married: `summer_9`, `winter_30` (NPC) |")
    lines.append("")
    lines.append("## 10. Приоритет 2 — намеренно НЕ закрыто")
    lines.append("")
    lines.append("| Ключи / зона | Почему оставлено |")
    lines.append("|--------------|------------------|")
    lines.append("| `spring_1`…`spring_28` (кроме фестивальных дат) | Уже в `harvey_married` FarmHouse — отдельный контекст дома, дубли NPC не нужны |")
    lines.append("| `Mon4`–`Sun6` без Dating/Married | При 4–7 ❤ блок с «ты» достаточен; при Dating игра берёт `Mon8`/`Mon10` |")
    lines.append("| `Beach`, `ArchaeologyHouse` (базовые) | Topic-overlay + 6–10 ❤; отдельный Dating не нужен |")
    lines.append("| `Resort_*` кроме `Resort` | Уже есть Dating/Married на под-ключах |")
    lines.append("| `spring_12`, `summer_10`, … (фестивали) | Уже Dating + частично Married в FarmHouse; base формальный, но перекрывается |")
    lines.append("| `spring_13` без 3–5 ❤ | Отдельная 8–10/Dating линия; 3–5 не срабатывает на этом ключе в игре |")
    lines.append("| `0–2 ❤` для сезонных/локаций | Низкий hearts редко видит эти ключи; base «Вы» приемлем |")
    lines.append("| `Saloon*`, `GreenRain`, фестивальные вторые дни | Dating уже в `harvey_dating`; Married — в FarmHouse или низкий приоритет тона |")
    lines.append("| `Hospital8`/`10`, `situationReaction_Drunk` Married | Следующий проход (не P2) |")
    lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT}")
    print(
        f"Keys: {len(all_keys)}, base-no-dating: {len(base_no_dating)}, topics base-only: {len(only_base)}"
    )


if __name__ == "__main__":
    main()
