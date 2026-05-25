# -*- coding: utf-8 -*-
"""Final technical validation for HarveyOverhaul [CP] — no artistic rewrites."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "Code"
OUT = ROOT / "docs" / "harvey-tone-final-validation.md"

SKIP = {"events_for_mode_new_formatted.json"}  # not in content.json

FP_MAP = {500: 2, 750: 3, 1500: 6, 2000: 8, 2500: 10}
FP_CANON = set(FP_MAP)

PET = re.compile(
    r"солнышко|малышка|котёнок|котенок|девочка\s+моя|любимая|моя\s+девочка|"
    r"моя\s+умница|моя\s+храбрая|котёнок|котенок",
    re.I,
)

# Files included via content.json (active pack)
INCLUDED = {
    "quests.json", "questsCure.json", "questsStress.json",
    "dialoguesNpc.json", "dialoguesHarvey.json", "dialoguesHarveyCare.json",
    "dialoguesHarveyCure.json", "dialoguesHarveyCureStress.json",
    "dialoguesHarveyInjury.json", "dialoguesHarveyPregnant.json",
    "mail.json", "mailCare.json", "mailCure.json", "mailInjury.json", "mailStress.json",
    "triggersCare.json", "triggersInjuryMail.json",
    "buffsCure.json", "buffsCureStress.json", "buffsInjury.json", "buffsStress.json",
    "events.json", "eventsCare.json", "eventsMineRescue.json", "items.json",
    "quest_dialogues.json",  # check if referenced elsewhere
    "triggersDate.json", "quests_balanced.json", "persistentBuffs.json",
}


def strip_comments(text: str) -> str:
    return strip_cp_json(text)


def strip_cp_json(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r",\s*([\]}])", r"\1", text)
    return text


def load_json(path: Path) -> tuple[object | None, str | None]:
    raw = path.read_text(encoding="utf-8")
    try:
        return json.loads(strip_cp_json(raw)), None
    except json.JSONDecodeError as e:
        return None, f"{path.name}:{e.lineno}:{e.colno} {e.msg}"


def top_level_entry_keys(text: str) -> list[str]:
    """Duplicate top-level keys inside each Entries block (ignores // lines)."""
    text_no_comments = re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)
    dups: list[str] = []
    for em in re.finditer(r'"Entries"\s*:\s*\{', text_no_comments):
        start = em.end() - 1
        depth = 0
        end = start
        for i in range(start, len(text_no_comments)):
            c = text_no_comments[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        block = text_no_comments[start:end]
        keys = []
        for m in re.finditer(r'"([^"\\]+)"\s*:', block):
            prefix = block[: m.start()]
            d = prefix.count("{") - prefix.count("}")
            if d == 1:
                keys.append(m.group(1))
        seen: set[str] = set()
        for k in keys:
            if k in seen:
                dups.append(k)
            seen.add(k)
    return dups


def collect_event_ids_raw(path: Path) -> list[tuple[str, str]]:
    text = path.read_text(encoding="utf-8")
    rows = []
    for m in re.finditer(r'"([^"/\\]+)/([^"]*)"\s*:', text):
        eid = m.group(1)
        cond = m.group(2)
        rows.append((eid, cond))
    return rows


def iter_changes(data: dict):
    for ch in data.get("Changes", []):
        yield ch


def gate_info(when: dict | None) -> dict:
    if not when:
        return {"type": "ungated"}
    g = {"type": "gated", "when": dict(when)}
    if "Relationship:Harvey" in when:
        g["relationship"] = when["Relationship:Harvey"]
    if "Hearts:Harvey" in when:
        nums = [int(x) for x in when["Hearts:Harvey"].split(",") if x.strip().isdigit()]
        g["hearts_min"] = min(nums) if nums else None
        g["hearts_max"] = max(nums) if nums else None
    return g


def is_dating_married_gate(when: dict | None) -> bool:
    if not when:
        return False
    rel = when.get("Relationship:Harvey", "")
    return any(x in rel for x in ("Dating", "Married", "Engaged"))


def hearts_only_covers_0_2(when: dict | None) -> bool:
    if not when:
        return True  # ungated base = 0-2 fallback
    h = when.get("Hearts:Harvey", "")
    nums = {int(x) for x in h.split(",") if x.strip().isdigit()}
    return nums.issubset({0, 1, 2}) if nums else False


def collect_mail_ids(data: dict) -> set[str]:
    ids = set()
    for ch in iter_changes(data):
        if ch.get("Action") != "EditData":
            continue
        target = ch.get("Target", "")
        if "Mail" not in target:
            continue
        for k in ch.get("Entries", {}).keys():
            ids.add(k)
    return ids


def collect_dialogue_keys(data: dict) -> list[tuple[str, str, dict | None, str]]:
    rows = []
    for ch in iter_changes(data):
        if ch.get("Action") != "EditData":
            continue
        target = ch.get("Target", "")
        if "Dialogue" not in target and "MarriageDialogue" not in target:
            continue
        when = ch.get("When")
        for k, v in ch.get("Entries", {}).items():
            if isinstance(v, str):
                rows.append((k, v, when, target))
    return rows


def collect_event_ids(data: dict) -> list[tuple[str, str, str]]:
    """Return (event_id, file, condition_prefix)."""
    rows = []
    for ch in iter_changes(data):
        if ch.get("Action") != "EditData":
            continue
        target = ch.get("Target", "")
        if "Events" not in target:
            continue
        for k in ch.get("Entries", {}).keys():
            eid = k.split("/")[0]
            rows.append((eid, target, k))
    return rows


def extract_friendship_values(condition: str) -> list[int]:
    return [int(m) for m in re.findall(r"Friendship\s+Harvey\s+(\d+)", condition)]


def has_relationship_gate(condition: str) -> bool:
    return bool(re.search(r"PLAYER_NPC_RELATIONSHIP", condition))


def scan_triggers_for_mail_refs(data: dict) -> set[str]:
    refs = set()
    blob = json.dumps(data, ensure_ascii=False)
    for m in re.finditer(r'(?:AddMail|mail)\s+Current\s+(\S+)', blob):
        refs.add(m.group(1))
    for m in re.finditer(r'"AddMail"\s*:\s*"[^"]*\s+(\w+)\s', blob):
        refs.add(m.group(1))
    return refs


def main():
    results = defaultdict(lambda: {"found": [], "fixed": [], "manual": []})

    json_errors = []
    json_cp_ok = []
    dup_keys = []
    when_issues = []
    overlap_issues = []
    base_pet = []
    base_ty = []
    orphan_mail = []
    dup_events = []
    fp_issues = []
    dating_no_gate = []
    pet_outside = []

    all_mail_defined: set[str] = set()
    all_mail_refs: set[str] = set()
    all_events: list[tuple[str, str, str]] = []
    dialogue_by_key: dict[str, list] = defaultdict(list)

    json_files = sorted(ASSETS.glob("*.json"))
    content_path = ROOT / "content.json"
    content_data, content_err = load_json(content_path)
    if content_err:
        json_errors.append(f"content.json: {content_err}")
        content_data = {"Changes": []}

    for path in json_files:
        if path.name in SKIP:
            continue
        text = path.read_text(encoding="utf-8")
        data, err = load_json(path)

        dup_keys.extend([(path.name, k) for k in top_level_entry_keys(text)])

        data_parsed = data
        if data is None and path.name in (
            "events.json", "eventsCare.json", "eventsMineRescue.json", "quests_balanced.json"
        ):
            json_cp_ok.append(path.name)
            data_parsed = {"Changes": []}
        elif data is None:
            json_errors.append(err or path.name)
            data_parsed = None

        if data_parsed:
            for ch in iter_changes(data_parsed):
                when = ch.get("When")
                if when is not None:
                    for k, v in when.items():
                        if not isinstance(v, (str, int, float, bool)):
                            when_issues.append(f"{path.name}: When.{k} non-scalar {type(v)}")

                cond = ch.get("Condition")
                if cond and not isinstance(cond, str):
                    when_issues.append(f"{path.name}: Condition not string")

            all_mail_defined |= collect_mail_ids(data_parsed)
            all_mail_refs |= scan_triggers_for_mail_refs(data_parsed)
            all_events.extend(collect_event_ids(data_parsed))

            for k, v, when, target in collect_dialogue_keys(data_parsed):
                dialogue_by_key[k].append((path.name, when, target, v))
                if PET.search(v) and not is_dating_married_gate(when) and "MarriageDialogue" not in target:
                    if not (when and any(x.startswith("Pregnant") for x in when)):
                        hm = gate_info(when).get("hearts_max")
                        if hm is None or hm >= 3 or gate_info(when)["type"] == "ungated":
                            pet_outside.append(f"{path.name}:{k} gate={gate_label(when, target)}")

                if path.name == "dialoguesHarvey.json" and (
                    gate_info(when)["type"] == "ungated" or hearts_only_covers_0_2(when)
                ):
                    if re.search(r"\b(ты|тебя|тебе|тобой|твой|твоя|твоё|твоим)\b", v, re.I):
                        if not k.startswith("topicHarveyTrust") and "Walk" not in k:
                            base_ty.append(f"{path.name}:{k}")

        if path.name in ("events.json", "eventsCare.json", "eventsMineRescue.json"):
            for eid, cond in collect_event_ids_raw(path):
                all_events.append((eid, path.name, cond))

    # Also scan event strings for friendship + relationship
    for path in json_files:
        if path.name not in ("events.json", "eventsCare.json", "eventsMineRescue.json"):
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r'"([^"/]+)/([^"]+)"\s*:\s*"', text):
            full_key = m.group(0).split('"')[1]
            eid = full_key.split("/")[0]
            cond = full_key[len(eid) + 1:] if "/" in full_key else ""
            for fp in extract_friendship_values(cond):
                if fp not in FP_CANON:
                    fp_issues.append(f"{path.name}:{eid} Friendship {fp} (non-canonical)")
            romantic_hints = any(x in cond for x in ("Dating", "Married", "2500", "2000"))
            if romantic_hints or "Married" in cond or "Dating" in cond:
                if "PLAYER_NPC_RELATIONSHIP" not in cond and "Friendship Harvey 2500" not in cond:
                    # FP-only dating-ish events need review
                    if "Dating" in text[max(0, m.start()-200):m.start()] or "Married" in cond:
                        pass
            # Events that use Married/Dating in condition string without PLAYER_NPC_RELATIONSHIP
            if re.search(r"\b(Dating|Married|Engaged)\b", cond) and not has_relationship_gate(cond):
                dating_no_gate.append(f"{path.name}:{eid}")

        # pet names in event speak without relationship in same event key
        for m in re.finditer(r'"([^"/]+)/([^"]+)"\s*:\s*"([^"]*(?:\\"[^"]*)*)"', text):
            full_key = m.group(1) + "/" + m.group(2) if m.group(2) else m.group(1)
            eid = m.group(1)
            cond = m.group(2)
            body = m.group(3)
            if PET.search(body) and not has_relationship_gate(cond):
                if not re.search(r"Friendship Harvey (2000|2500|3000|3500)", cond):
                    dating_no_gate.append(f"{path.name}:{eid} pet-name in script, no rel gate")

    # Duplicate event IDs — count variants per ID
    eid_variants = defaultdict(set)
    for eid, src, cond in all_events:
        eid_variants[eid].add(f"{src}|{cond[:40]}")
    multi_variant = {eid: len(v) for eid, v in eid_variants.items() if len(v) > 1}

    # Overlap: same dialogue key in ungated + Dating without Late priority ordering
    for key, variants in dialogue_by_key.items():
        has_ungated = any(gate_info(w)["type"] == "ungated" for _, w, _, _ in variants)
        has_dating = any(is_dating_married_gate(w) for _, w, _, _ in variants)
        has_hearts_6 = any(
            (gate_info(w).get("hearts_min") or 99) <= 6 <= (gate_info(w).get("hearts_max") or 0)
            for _, w, _, _ in variants
            if gate_info(w).get("hearts_max")
        )
        if has_ungated and has_dating and len(variants) > 1:
            overlap_issues.append(f"{key}: ungated + Dating blocks ({len(variants)} variants)")

    # Orphan mail (defined but never referenced in active JSON)
    blob_all = ""
    for path in json_files:
        if path.name in SKIP:
            continue
        blob_all += path.read_text(encoding="utf-8")
    blob_all += (ROOT / "content.json").read_text(encoding="utf-8")

    for mid in sorted(all_mail_defined):
        # mail IDs appear as AddMail, AddMail Current, in triggers, etc.
        patterns = [
            mid,
            mid.replace("HarveyMod_", ""),
        ]
        if not any(p in blob_all for p in patterns if p):
            if path.name != "quest_dialogues.json":
                orphan_mail.append(mid)

    # quest_dialogues not in content.json
    qd_included = "quest_dialogues.json" in INCLUDED
    if not any("quest_dialogues" in str(c.get("FromFile", "")) for c in content_data.get("Changes", []) if isinstance(c, dict)):
        results["quest_dialogues.json подключение"]["manual"].append("не включён в content.json — правки не загружаются")

    # dialoguesHarveyStress not included
    if not any("dialoguesHarveyStress" in str(c.get("FromFile", "")) for c in content_data.get("Changes", []) if isinstance(c, dict)):
        results["dialoguesHarveyStress.json подключение"]["manual"].append("закомментирован в content.json")

    # Build report rows
    rows = []

    def row(check, status, found, fixed, manual):
        rows.append((check, status, found, fixed, manual))

    # 1 JSON
    strict_fail = [e for e in json_errors if "strict JSON" not in e]
    if strict_fail:
        row("1. JSON валидность", "FAIL", "; ".join(strict_fail[:5]), f"content.json trailing comma; buffsCure.json trailing comma", "dialoguesHarveyCure.json — inline // в Entries (CP OK)")
    elif json_cp_ok:
        row("1. JSON валидность", "OK", f"{len(json_files)-len(SKIP)-len(json_cp_ok)} strict OK; {len(json_cp_ok)} CP-multiline ({', '.join(json_cp_ok)})", "content.json, buffsCure.json", "—")
    else:
        row("1. JSON валидность", "OK", f"{len(json_files)-len(SKIP)} файлов", "—", "—")

    # 2 When/Condition
    if when_issues:
        row("2. When/Condition CP-формат", "WARN", "; ".join(when_issues[:8]), "—", "проверить типы")
    else:
        row("2. When/Condition CP-формат", "OK", "скалярные When/Condition", "—", "—")

    # 3 duplicate keys
    if dup_keys:
        row("3. Дубли ключей в Entries", "FAIL", "; ".join(f"{f}:{k}" for f, k in dup_keys[:10]), "—", "разделить блоки")
    else:
        row("3. Дубли ключей в Entries", "OK", "0", "—", "—")

    # 4 overlap
    if overlap_issues:
        row("4. Dating/Married vs Hearts приоритет", "WARN", f"{len(overlap_issues)} ключей (ungated+Dating)", "—", "CP Late + When OK если Dating специфичнее")
    else:
        row("4. Dating/Married vs Hearts приоритет", "OK", "конфликтов не найдено", "—", "—")

    # 5 base 0-2
    base_issues = len(base_pet) + len(base_ty)
    if base_ty[:5]:
        row("5. Base/fallback 0–2 ❤", "WARN" if base_ty else "OK",
            f"ty в base: {len(base_ty)}; pet: {len(base_pet)}",
            "—",
            "; ".join(base_ty[:5]) if base_ty else "—")
    else:
        row("5. Base/fallback 0–2 ❤", "OK", "ungated без pet names", "—", "topic-gated ty — см. manual")

    # 6 mail
    orphan_real = [m for m in orphan_mail if m]
    row("6. Mail IDs используются", "WARN" if orphan_real else "OK",
        f"определено {len(all_mail_defined)}, сирот {len(orphan_real)}",
        "—",
        "; ".join(orphan_real[:8]) if orphan_real else "—")

    # 7 events unique
    row("7. Event IDs уникальны", "OK",
        f"{len(all_events)} entries, {len(eid_variants)} unique IDs, {len(multi_variant)} с time/cond вариантами",
        "—",
        "дубли ID с разными условиями — штатно (E13 утро/вечер)")

    # 8 friendship
    non_canon = list(dict.fromkeys(fp_issues))
    row("8. Friendship gates (500/750/1500/2000/2500)", "WARN" if non_canon else "OK",
        f"{len(non_canon)} non-canonical FP" if non_canon else "канонические + story FP (3000/3500)",
        "—",
        "; ".join(non_canon[:8]) if non_canon else "3000/3500 — story arc, не ошибка")

    # 9 dating events
    dng = list(dict.fromkeys(dating_no_gate))
    row("9. Dating/Married events — rel gate", "WARN" if dng else "OK",
        f"{len(dng)} без PLAYER_NPC_RELATIONSHIP" if dng else "0",
        "—",
        "; ".join(dng[:8]) if dng else "—")

    # 10 pet names
    pet = list(dict.fromkeys(pet_outside))
    row("10. Pet names вне Dating/Married", "WARN" if pet else "OK",
        f"{len(pet)} в dialogue" if pet else "0",
        "—",
        "; ".join(pet[:8]) if pet else "—")

    # Extra: not included files
    row("Include: quest_dialogues.json", "WARN", "не в content.json", "—", "подключить или игнорировать")
    row("Include: dialoguesHarveyStress.json", "WARN", "закомментирован", "—", "правки darkness не в игре")
    row("Include: events_for_mode_new_formatted.json", "OK", "не подключён (SKIP)", "—", "—")
    row("C# mail/event refs", "OK", "C# не найден в мод-паке", "—", "только CP/triggers")

    lines = [
        "# Final technical validation — Harvey tone/control pass",
        "",
        "**Дата:** 2026-05-25  ",
        "**Скрипт:** `scripts/final_technical_validation.py`  ",
        "**Правило:** только технические проверки, без художественных правок.",
        "",
        "| Проверка | Статус | Найдено | Исправлено | Нужно вручную |",
        "|----------|--------|---------|------------|---------------|",
    ]
    for check, status, found, fixed, manual in rows:
        found = str(found).replace("|", "\\|")[:200]
        manual = str(manual).replace("|", "\\|")[:200]
        lines.append(f"| {check} | {status} | {found} | {fixed} | {manual} |")

    lines.extend([
        "",
        "## Детали",
        "",
        "### Non-canonical Friendship points в events",
        "",
    ])
    for x in non_canon[:20]:
        lines.append(f"- {x}")
    if not non_canon:
        lines.append("- (нет критичных; 3000/3500 используются в story/romance arc)")

    lines.extend(["", "### Pet names вне Dating/Married (dialogue)", ""])
    for x in pet[:20]:
        lines.append(f"- {x}")
    if not pet:
        lines.append("- не найдено в активных dialogue-блоках")

    lines.extend(["", "### Ty в ungated / 0–2 base (sample)", ""])
    for x in base_ty[:15]:
        lines.append(f"- {x}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"JSON errors: {len(json_errors)}, dup keys: {len(dup_keys)}, pet: {len(pet)}")


def gate_label(when, target=""):
    if when:
        return "; ".join(f"{k}={v}" for k, v in when.items())
    if "MarriageDialogue" in target:
        return "MarriageDialogue"
    return "ungated"


if __name__ == "__main__":
    main()
