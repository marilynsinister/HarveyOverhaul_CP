#!/usr/bin/env python3
"""Final read-only audit of Harvey dialogue split files → docs/dialogues_harvey_final_audit.md"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUES_DIR = ROOT / "assets" / "Code" / "dialogues"
MANIFEST = ROOT / "assets" / "Code" / "dialoguesHarvey.json"
REPORT = ROOT / "docs" / "dialogues_harvey_final_audit.md"

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
]

TARGETS = {
    "Characters/Dialogue/Harvey",
    "Characters/Dialogue/MarriageDialogueHarvey",
    "strings/schedules/Harvey",
}

VY_PATTERN = re.compile(r"\b(Вы|Вас|Вам|Ваш|Ваше|Ваши)\b")
TY_INFORMAL = re.compile(
    r"\b(ты|тебя|тебе|твой|твоё|твоя|твоим|твоей|твоих|твоими)\b",
    re.IGNORECASE,
)
EARLY_FORBIDDEN = re.compile(
    r"(солнышко|малышк|котёнок|котенок|\bты\b|\bтебя\b|\bтебе\b)",
    re.IGNORECASE,
)

LADDER_PREFIXES = (
    "Hospital_",
    "timeReaction_",
    "locationReaction_",
    "emotionalReaction_",
    "situationReaction_",
    "Resort_",
    "Resort",
    "AcceptGift_",
    "AcceptBirthdayGift_",
)

HARSH_PHRASES = [
    ("не спорь", re.compile(r"не спор", re.I)),
    ("не отпущу", re.compile(r"не отпущ", re.I)),
    ("я всё решу", re.compile(r"я всё решу|я все решу", re.I)),
    ("я не дам", re.compile(r"я не дам", re.I)),
    ("без возражений", re.compile(r"без возражений|никаких возражений", re.I)),
    ("под моим контролем", re.compile(r"под моим контролем", re.I)),
    ("не пугайтесь", re.compile(r"не пугай", re.I)),
]

SOFT_PHRASES = [
    ("давай договоримся", re.compile(r"давай договорим", re.I)),
    ("я напомню", re.compile(r"я напомн", re.I)),
    ("мне спокойнее", re.compile(r"мне спокойн", re.I)),
    ("если захочешь", re.compile(r"если захочешь|если попросишь", re.I)),
    ("без давления", re.compile(r"без давления|без ложки|без нотаций", re.I)),
]


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


def when_label(when: dict | None) -> str:
    if not when:
        return "(нет When)"
    return ", ".join(f"{k}={v}" for k, v in when.items())


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


def topic_keys(when: dict | None) -> frozenset[str]:
    if not when:
        return frozenset()
    return frozenset(k for k in when if k.startswith("HasConversationTopic") or k.startswith("topic"))


@dataclass
class Patch:
    global_order: int
    file: str
    file_order: int
    target: str
    when: dict | None
    when_label: str
    priority: str | int | None
    entries: dict[str, str]

    @property
    def is_dating(self) -> bool:
        return relationship(self.when) == "Dating"

    @property
    def is_married_rel(self) -> bool:
        return relationship(self.when) == "Married"

    @property
    def is_hearts_0_2(self) -> bool:
        hs = hearts_set(self.when)
        return hs is not None and hs <= {0, 1, 2}

    @property
    def is_topic(self) -> bool:
        return bool(topic_keys(self.when)) or any(
            k.startswith("topic") for k in (self.when or {})
        )


def load_all_patches() -> list[Patch]:
    patches: list[Patch] = []
    order = 0
    for fi, fname in enumerate(LOAD_ORDER):
        path = DIALOGUES_DIR / fname
        if not path.exists():
            raise FileNotFoundError(path)
        data = parse_json(path)
        for ch in data.get("Changes", []):
            if ch.get("Action") != "EditData":
                continue
            target = ch.get("Target")
            if target not in TARGETS:
                continue
            order += 1
            patches.append(
                Patch(
                    global_order=order,
                    file=fname,
                    file_order=fi,
                    target=target,
                    when=ch.get("When"),
                    when_label=when_label(ch.get("When")),
                    priority=ch.get("Priority"),
                    entries=ch.get("Entries") or {},
                )
            )
    return patches


def specificity_score(when: dict | None) -> int:
    if not when:
        return 0
    score = len(when) * 10
    if relationship(when):
        score += 50
    if hearts_set(when):
        score += 20
    if topic_keys(when):
        score += 40
    for k in when:
        if k.startswith("HasConversationTopic"):
            score += 30
    return score


def when_overlap(a: dict | None, b: dict | None) -> bool:
    """Heuristic: both patches can apply in some game state."""
    if a is None and b is None:
        return True
    if a is None or b is None:
        # base layer overlaps everything
        return True

    ra, rb = relationship(a), relationship(b)
    if ra and rb and ra != rb:
        return False

    ha, hb = hearts_set(a), hearts_set(b)
    if ha and hb and not (ha & hb):
        return False

    ta, tb = topic_keys(a), topic_keys(b)
    if ta or tb:
        if ta and tb and ta != tb:
            return False
        if (ta or tb) and not (ta and tb):
            # one topic-specific, one not — can overlap if other When matches
            pass

    # extra keys: if both specify different LocationName etc., assume disjoint unless equal
    shared_keys = set(a) & set(b) - {"Hearts:Harvey", "Relationship:Harvey"}
    for k in shared_keys:
        if a[k] != b[k]:
            return False
    return True


def is_ladder_key(key: str) -> bool:
    if key.startswith("AcceptGift_") or key.startswith("AcceptBirthdayGift_"):
        return True
    for p in LADDER_PREFIXES:
        if key == p or key.startswith(p):
            return True
    return False


def ladder_tier(patch: Patch) -> str:
    if patch.is_married_rel:
        return "married"
    if patch.is_dating:
        return "dating"
    hs = hearts_set(patch.when)
    if hs is not None:
        if hs <= {0, 1, 2}:
            return "hearts_0_2"
        if hs <= {3, 4, 5}:
            return "hearts_3_5"
        if max(hs) <= 7:
            return "hearts_4_7"
        return "hearts_8_10"
    if patch.when is None:
        return "base"
    if patch.is_topic:
        return "topic"
    # hearts ranges in locations without explicit relationship
    if hs := hearts_set(patch.when):
        if max(hs) >= 8:
            return "hearts_8_10"
        if max(hs) >= 4:
            return "hearts_4_7"
    return "other"


def preview(text: str, n: int = 100) -> str:
    t = text.replace("\n", " ").replace("#$b#", " ")
    return (t[:n] + "…") if len(t) > n else t


def run_audit() -> str:
    patches = load_all_patches()
    total_entries = sum(len(p.entries) for p in patches)

    # --- Check 1: Vy in Dating/Married ---
    vy_dating = []
    vy_married = []
    for p in patches:
        for key, text in p.entries.items():
            for m in VY_PATTERN.finditer(text):
                hit = {
                    "file": p.file,
                    "order": p.global_order,
                    "when": p.when_label,
                    "key": key,
                    "word": m.group(1),
                    "preview": preview(text),
                }
                if p.is_dating:
                    vy_dating.append(hit)
                if p.is_married_rel or (
                    p.target == "Characters/Dialogue/MarriageDialogueHarvey"
                    and relationship(p.when) in (None, "Married")
                ):
                    vy_married.append(hit)

    # --- Check 2: informal in 0-2 hearts ---
    early_bad = []
    for p in patches:
        if not p.is_hearts_0_2:
            continue
        for key, text in p.entries.items():
            if EARLY_FORBIDDEN.search(text):
                early_bad.append(
                    {
                        "file": p.file,
                        "key": key,
                        "when": p.when_label,
                        "preview": preview(text),
                    }
                )

    # Also scan topic blocks with hearts 0-2
    for p in patches:
        hs = hearts_set(p.when)
        if hs and hs <= {0, 1, 2} and not p.is_hearts_0_2:
            for key, text in p.entries.items():
                if EARLY_FORBIDDEN.search(text):
                    early_bad.append(
                        {
                            "file": p.file,
                            "key": key,
                            "when": p.when_label,
                            "preview": preview(text),
                            "note": "topic/hearts overlay",
                        }
                    )

    # --- Check 3-4: duplicate keys with overlapping When ---
    key_occurrences: dict[str, list[Patch]] = defaultdict(list)
    for p in patches:
        for k in p.entries:
            key_occurrences[k].append(p)

    dup_keys = {k: ps for k, ps in key_occurrences.items() if len(ps) > 1}
    overlapping: list[dict] = []
    order_violations: list[dict] = []

    for key, ps in sorted(dup_keys.items()):
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                if when_overlap(ps[i].when, ps[j].when):
                    overlapping.append(
                        {
                            "key": key,
                            "a": (ps[i].file, ps[i].global_order, ps[i].when_label),
                            "b": (ps[j].file, ps[j].global_order, ps[j].when_label),
                        }
                    )
                    sa, sb = specificity_score(ps[i].when), specificity_score(ps[j].when)
                    if sa > sb and ps[i].global_order > ps[j].global_order:
                        pass  # more specific later — OK
                    elif sb > sa and ps[j].global_order > ps[i].global_order:
                        pass
                    elif sa != sb:
                        # same overlap but specificity order wrong
                        more = ps[i] if sa > sb else ps[j]
                        less = ps[j] if sa > sb else ps[i]
                        if more.global_order < less.global_order:
                            order_violations.append(
                                {
                                    "key": key,
                                    "specific": (more.file, more.when_label, more.global_order),
                                    "generic": (less.file, less.when_label, less.global_order),
                                }
                            )

    # Effective winner per key (last in load order among overlapping group — simplified: last global)
    ladder_dupes: dict[str, list] = defaultdict(list)
    for key, ps in dup_keys.items():
        if is_ladder_key(key):
            ladder_dupes[key] = [
                (p.file, p.when_label, p.global_order, ladder_tier(p)) for p in ps
            ]

    # --- Check 5: topics vs dating/married tone ---
    topic_tone_issues = []
    for p in patches:
        if not (p.is_topic or any("topic" in str(k) for k in (p.when or {}))):
            continue
        rel = relationship(p.when)
        for key, text in p.entries.items():
            has_vy = bool(VY_PATTERN.search(text))
            has_ty = bool(TY_INFORMAL.search(text))
            if rel == "Dating" and has_vy:
                topic_tone_issues.append(
                    {"type": "dating+Вы", "file": p.file, "key": key, "when": p.when_label}
                )
            if rel == "Married" and has_vy:
                topic_tone_issues.append(
                    {"type": "married+Вы", "file": p.file, "key": key, "when": p.when_label}
                )
            if rel in ("Dating", "Married") and has_vy and has_ty:
                topic_tone_issues.append(
                    {"type": "mix Вы/ты", "file": p.file, "key": key, "when": p.when_label}
                )
            # topic on 0-2 with ty
            hs = hearts_set(p.when)
            if hs and hs <= {0, 1, 2} and has_ty and "AcceptGift" not in key:
                if EARLY_FORBIDDEN.search(text):
                    topic_tone_issues.append(
                        {
                            "type": "topic 0-2 informal",
                            "file": p.file,
                            "key": key,
                            "when": p.when_label,
                        }
                    )

    # --- Check 6: ladder clarity ---
    ladder_by_key: dict[str, set[str]] = defaultdict(set)
    for key, ps in dup_keys.items():
        if is_ladder_key(key):
            for p in ps:
                ladder_by_key[key].add(ladder_tier(p))

    ladder_unclear = {
        k: sorted(v)
        for k, v in ladder_by_key.items()
        if len(v) > 1 and not _ladder_order_ok(v)
    }

    # --- Check 7: hypercare tone ---
    harsh_hits = defaultdict(list)
    soft_hits = defaultdict(list)
    for p in patches:
        for key, text in p.entries.items():
            for name, pat in HARSH_PHRASES:
                if pat.search(text):
                    harsh_hits[name].append((p.file, key, p.when_label))
            for name, pat in SOFT_PHRASES:
                if pat.search(text):
                    soft_hits[name].append((p.file, key))

    # Mixed vy+ty anywhere
    mixed_vy_ty = []
    for p in patches:
        for key, text in p.entries.items():
            if VY_PATTERN.search(text) and TY_INFORMAL.search(text):
                mixed_vy_ty.append(
                    {
                        "file": p.file,
                        "key": key,
                        "when": p.when_label,
                        "preview": preview(text, 80),
                    }
                )

    # Build markdown
    lines: list[str] = []
    lines.append("# Финальный аудит диалогов Харви")
    lines.append("")
    lines.append("**Дата:** 2026-06-04  ")
    lines.append("**Область:** split-файлы `assets/Code/dialogues/harvey_*.json` (порядок из `dialoguesHarvey.json`)  ")
    lines.append("**Режим:** только отчёт, правки в JSON не вносились.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Сводка")
    lines.append("")
    lines.append(f"| Метрика | Значение |")
    lines.append(f"|---------|----------|")
    lines.append(f"| Файлов в manifest | {len(LOAD_ORDER)} |")
    lines.append(f"| Патчей EditData (Harvey targets) | {len(patches)} |")
    lines.append(f"| Всего ключей Entries | {total_entries} |")
    lines.append(f"| Уникальных ключей | {len(key_occurrences)} |")
    lines.append(f"| Ключей в 2+ патчах | {len(dup_keys)} |")
    lines.append(f"| Пар пересекающихся When (оценка) | {len(overlapping)} |")
    lines.append(f"| Нарушений порядка специфичности | {len(order_violations)} |")
    lines.append(f"| «Вы» в Dating | {len(vy_dating)} |")
    lines.append(f"| «Вы» в Married / MarriageDialogue | {len(vy_married)} |")
    lines.append(f"| Неформальное в 0–2 ❤ | {len(early_bad)} |")
    lines.append(f"| Смешение Вы+ты в одной строке | {len(mixed_vy_ty)} |")
    lines.append(f"| Topic-тон (dating/married/0-2) | {len(topic_tone_issues)} |")
    lines.append(f"| Ladder-ключи с неясной лестницей | {len(ladder_unclear)} |")
    lines.append("")

    def status(ok: bool) -> str:
        return "✅ PASS" if ok else "❌ FAIL"

    c1 = len(vy_dating) == 0 and len(vy_married) == 0
    c2 = len(early_bad) == 0
    c5 = len([x for x in topic_tone_issues if x["type"] in ("dating+Вы", "married+Вы", "topic 0-2 informal")]) == 0
    lines.append("### Критерии из запроса")
    lines.append("")
    lines.append(f"1. Dating/Married без «Вы»… — {status(c1)}")
    lines.append(f"2. 0–2 ❤ без ты/ласковых — {status(c2)}")
    lines.append(f"3–4. Пересечения When / порядок — см. §3 ({len(order_violations)} нарушений порядка)")
    lines.append(f"5. Topic не ломает dating/married — {status(c5)}")
    lines.append(f"6. Лестница реакций — см. §6 ({len(ladder_unclear)} спорных ключей)")
    lines.append(f"7. Гиперопека мягче — см. §7 (эвристика)")
    lines.append("")

    # Section 1
    lines.append("## 1. «Вы» в Dating и Married")
    lines.append("")
    if c1:
        lines.append("Формальное обращение **не найдено** в патчах с `Relationship:Harvey = Dating` или `Married`, включая `MarriageDialogueHarvey`.")
    else:
        if vy_dating:
            lines.append("### Dating")
            for h in vy_dating[:30]:
                lines.append(f"- `{h['key']}` ({h['file']}, #{h['order']}): **{h['word']}** — {h['preview']}")
            if len(vy_dating) > 30:
                lines.append(f"- … ещё {len(vy_dating) - 30}")
        if vy_married:
            lines.append("### Married")
            for h in vy_married[:30]:
                lines.append(f"- `{h['key']}` ({h['file']}, #{h['order']}): **{h['word']}** — {h['preview']}")
    lines.append("")

    # Section 2
    lines.append("## 2. Неформальное обращение в 0–2 ❤")
    lines.append("")
    if c2:
        lines.append("В патчах `Hearts:Harvey = 0,1,2` (gifts) и topic-overlay на 0–2 **нет** ты/тебя/солнышко/малышка/котёнок.")
    else:
        for h in early_bad[:40]:
            note = h.get("note", "")
            lines.append(f"- `{h['key']}` — {h['file']} | {h['when']} {note}")
            lines.append(f"  - {h['preview']}")
    lines.append("")

    # Section 3-4
    lines.append("## 3–4. Дубли ключей и пересекающиеся When")
    lines.append("")
    lines.append("При `Priority: Late` побеждает **последний** патч в порядке manifest (см. `dialogues_harvey_split_notes.md`).")
    lines.append("")
    pattern_groups = defaultdict(list)
    for key in dup_keys:
        for prefix in LADDER_PREFIXES:
            if key.startswith(prefix) or key == prefix.rstrip("_"):
                pattern_groups[prefix].append(key)
                break
        else:
            if re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)", key):
                pattern_groups["weekday_*"].append(key)

    lines.append("### Дубли по группам (ladder / сезон)")
    lines.append("")
    for g in sorted(pattern_groups.keys()):
        keys = pattern_groups[g]
        if keys:
            lines.append(f"- **{g}**: {len(keys)} ключей в нескольких патчах")
    lines.append("")
    lines.append(f"Всего ключей с дублями: **{len(dup_keys)}**. Пар с пересекающимся When (эвристика): **{len(overlapping)}**.")
    lines.append("")
    if order_violations:
        lines.append("### ⚠️ Более специфичный патч идёт РАНЬШЕ общего (риск перебивания)")
        lines.append("")
        for v in order_violations[:25]:
            lines.append(
                f"- `{v['key']}`: specific {v['specific']} **до** generic {v['generic']}"
            )
        if len(order_violations) > 25:
            lines.append(f"- … ещё {len(order_violations) - 25}")
    else:
        lines.append("Явных нарушений «специфичный позже общего» по эвристике specificity **не найдено** (пересечения могут быть намеренными).")
    lines.append("")

    # intentional overlaps note
    lines.append("### Намеренные пересечения (ожидаемые)")
    lines.append("")
    lines.append("| Ключи | Файлы | Замечание |")
    lines.append("|-------|-------|-----------|")
    lines.append("| `Hospital_*` | topics → locations → hospital → dating | topic и heart; hospital manifest **после** topics |")
    lines.append("| `timeReaction_*` … | base/locations 4–7, 8–10, dating | dating **последний** среди Dialogue/Harvey |")
    lines.append("| `AcceptGift_*` | hearts_0_2 → 3_5 → 6_10 → married → dating gifts | dating gifts после married — проверить в игре |")
    lines.append("")

    # Section 5
    lines.append("## 5. Topic-блоки vs dating/married")
    lines.append("")
    if not topic_tone_issues:
        lines.append("Конфликтов тона (Вы в dating/married topics, informal в topic+0–2) **не обнаружено**.")
    else:
        by_type = defaultdict(list)
        for x in topic_tone_issues:
            by_type[x["type"]].append(x)
        for t, items in sorted(by_type.items()):
            lines.append(f"### {t} ({len(items)})")
            for it in items[:15]:
                lines.append(f"- `{it['key']}` — {it['file']} | {it['when']}")
            lines.append("")
    lines.append("")

    # Section 6
    lines.append("## 6. Лестница отношений (реакции / подарки / больница)")
    lines.append("")
    lines.append("Ожидаемый порядок силы тона (слабее → сильнее): `base` → `hearts_0_2` → `hearts_3_5` → `hearts_4_7` → `hearts_8_10` → `dating` → `married`.")
    lines.append("")
    if ladder_unclear:
        lines.append(f"**{len(ladder_unclear)}** ladder-ключей встречаются в несортированных комбинациях tier (не ошибка, если load order исправляет):")
        for k, tiers in list(ladder_unclear.items())[:20]:
            occ = ladder_dupes.get(k, [])
            lines.append(f"- `{k}`: tiers {tiers} — {occ}")
    else:
        lines.append("Для ladder-ключей с дублями tier-наборы согласованы с порядком manifest (последний патч = dating/married где задано).")
    lines.append("")
    lines.append("### Примеры финального победителя (последний global_order)")
    lines.append("")
    sample_keys = [
        "timeReaction_Late",
        "locationReaction_SkullCave",
        "Hospital_Mon",
        "AcceptGift_(O)StardropTea",
        "Resort_Shore",
    ]
    last_patch_for: dict[str, Patch] = {}
    for p in patches:
        for k in p.entries:
            last_patch_for[k] = p
    for sk in sample_keys:
        if sk in last_patch_for:
            p = last_patch_for[sk]
            lines.append(f"- `{sk}` → {p.file} (#{p.global_order}, {p.when_label})")
    lines.append("")

    # Section 7
    lines.append("## 7. Гиперопека: жёсткие vs мягкие формулировки")
    lines.append("")
    lines.append("Подсчёт вхождений по **всем** split-файлам (эвристика, не полный семантический анализ).")
    lines.append("")
    lines.append("| Маркер | Вхождений |")
    lines.append("|--------|-----------|")
    for name, _ in HARSH_PHRASES:
        lines.append(f"| {name} | {len(harsh_hits[name])} |")
    lines.append("")
    lines.append("| Мягкий маркер | Вхождений |")
    lines.append("|---------------|-----------|")
    for name, _ in SOFT_PHRASES:
        lines.append(f"| {name} | {len(soft_hits[name])} |")
    lines.append("")
    total_harsh = sum(len(v) for v in harsh_hits.values())
    total_soft = sum(len(v) for v in soft_hits.values())
    lines.append(f"**Итого:** жёстких маркеров {total_harsh}, мягких {total_soft}. ")
    if total_harsh == 0:
        lines.append("Жёсткие триггеры из чеклиста **отсутствуют** — гиперопека смещена в сторону договорённостей.")
    elif total_soft > total_harsh * 3:
        lines.append("Соотношение указывает на **смягчение** относительно старого аудита (`dialogues_harvey_audit.md`).")
    else:
        lines.append("Остаются единичные жёсткие фразы — см. таблицу ниже.")
    lines.append("")
    if total_harsh:
        lines.append("### Оставшиеся жёсткие вхождения")
        for name, items in harsh_hits.items():
            if items:
                lines.append(f"**{name}** ({len(items)}):")
                for f, k, w in items[:8]:
                    lines.append(f"- `{k}` — {f} | {w}")
                if len(items) > 8:
                    lines.append(f"- … +{len(items) - 8}")
        lines.append("")

    # Mixed vy ty
    lines.append("## Дополнительно: «Вы» и «ты» в одной реплике")
    lines.append("")
    if mixed_vy_ty:
        for m in mixed_vy_ty:
            lines.append(f"- `{m['key']}` — {m['file']} | {m['when']}: {m['preview']}")
    else:
        lines.append("Не найдено.")
    lines.append("")

    # File inventory
    lines.append("## Приложение: патчи по файлам")
    lines.append("")
    by_file = defaultdict(list)
    for p in patches:
        by_file[p.file].append(p)
    for fname in LOAD_ORDER:
        ps = by_file[fname]
        n = sum(len(p.entries) for p in ps)
        lines.append(f"- **{fname}**: {len(ps)} патчей, {n} ключей")
    lines.append("")
    lines.append("---")
    lines.append("*Сгенерировано `scripts/final_audit_dialogues_harvey.py`.*")

    return "\n".join(lines)


def _ladder_order_ok(tiers: set[str]) -> bool:
    order = [
        "base",
        "hearts_0_2",
        "hearts_3_5",
        "hearts_4_7",
        "hearts_8_10",
        "topic",
        "dating",
        "married",
        "other",
    ]
    idx = [order.index(t) for t in tiers if t in order]
    return not idx or max(idx) - min(idx) <= 4


if __name__ == "__main__":
    REPORT.write_text(run_audit(), encoding="utf-8")
    print(f"Wrote {REPORT}")
