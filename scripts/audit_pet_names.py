# -*- coding: utf-8 -*-
"""Audit forbidden tone phrases; apply gate-aware fixes; write audit markdown."""
from __future__ import annotations

import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "Code"
OUT = ROOT / "docs" / "audit-pet-names-after-fix.md"

PHRASES = [
    "солнышко", "малышка", "котёнок", "котенок", "девочка моя", "моя девочка",
    "дорогая",
    "любимая", "люблю", "хрупк", "не отпущу", "не позволю", "под моей защитой",
]
PET = re.compile(r"солнышко|малышка|котёнок|котенок|девочка моя|моя девочка|любимая", re.I)
SKIP = {"events_for_mode_new_formatted.json"}


def strip_comments(text: str) -> str:
    return re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)


def gate_label(when: dict | None, target: str = "") -> str:
    if when:
        return "; ".join(f"{k}={v}" for k, v in when.items())
    if "MarriageDialogue" in target:
        return "MarriageDialogue (Married)"
    return "ungated"


def is_allowed_romance(when: dict | None, target: str = "") -> bool:
    if when:
        if when.get("Relationship:Harvey") in ("Dating", "Married"):
            return True
        if any(k.startswith("Pregnant") for k in when):
            return True
    if "MarriageDialogue" in target:
        return True
    return False


def is_severe_medical(key: str, text: str) -> bool:
    severe_keys = (
        "topicStressCritical", "topicStressCollapse", "topicStressDespair",
        "topicStressDarknessLevel3", "topicDarknessStep1Complete",
        "HarveyMod_DespairIntervention", "HarveyMod_SuicidalIdeation",
        "topicHarveyForcedHospitalization", "topicStressBreakdown",
        "topicStressPanic", "emotionalReaction_Scared",
    )
    return any(k in key for k in severe_keys) or "критическ" in text.lower()


def hearts_max(when: dict | None) -> int | None:
    if not when:
        return None
    h = when.get("Hearts:Harvey", "")
    nums = [int(x) for x in h.split(",") if x.strip().isdigit()]
    return max(nums) if nums else None


def fix_string(s: str, *, allowed_romance: bool, severe: bool, hearts: int | None) -> str:
    if not allowed_romance:
        s = PET.sub("@", s)
        s = re.sub(r",?\s*@(?=[,.!?#\$]|$)", "", s)
        s = re.sub(r"^@,\s*", "", s)
        s = re.sub(r"\bдорогая\b", "@", s, flags=re.I)
        s = re.sub(r"\bмоя\s+девочка\b", "@", s, flags=re.I)
        s = re.sub(r"\bмоя\s+жена\b", "@", s, flags=re.I)
        s = re.sub(r"\bмоя\s+храбрая\b", "@", s, flags=re.I)
        s = re.sub(r"\bмоя\s+умница\b", "@", s, flags=re.I)
        s = re.sub(r"\bмоя\s+драгоценн", "@", s, flags=re.I)
        s = re.sub(r"\bты\s+моя\b", "ты важна для меня", s, flags=re.I)
        s = re.sub(r"\bлюблю\s+тебя\b", "мне не всё равно", s, flags=re.I)
        s = re.sub(r"\bочень\s+тебя\s+люблю\b", "очень о тебе забочусь", s, flags=re.I)
        s = re.sub(r",\s*который очень тебя любит", ", который очень о тебе заботится", s, flags=re.I)

    # хрупкая о личности
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого|ая)\s+девушк", r"уставш\1 девушк", s, flags=re.I)
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого)\s+и\s+бледн", r"уставш\1 и бледн", s, flags=re.I)
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого)\s+и\s+нежн", r"уставш\1 и нежн", s, flags=re.I)
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого)\s+и\s+светл", r"уставш\1 и светл", s, flags=re.I)
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого)\s+и\s+тих", r"уставш\1 и тих", s, flags=re.I)
    s = re.sub(r"Ты\s+очень\s+хрупкая", "Ты выглядишь очень уставшей", s)
    s = re.sub(r"ты\s+очень\s+хрупкая", "ты выглядишь очень уставшей", s)
    s = re.sub(r"такая\s+хрупкая", "такая уставшая", s, flags=re.I)
    s = re.sub(r"очень\s+хрупкая", "очень уставшая", s, flags=re.I)
    s = re.sub(r"слишком\s+хрупкая", "слишком уставшая", s, flags=re.I)
    s = re.sub(r"хрупкая\s+душа", "уставшая душа", s, flags=re.I)
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого)\s+природ", r"чувствительн\1 природ", s, flags=re.I)
    s = re.sub(r"твоей\s+хрупкости", "твоего состояния", s, flags=re.I)
    s = re.sub(r"с\s+твоей\s+хрупкостью", "в твоём состоянии", s, flags=re.I)
    s = re.sub(r"хрупк(им|ой|ая|ую|ие|ого)\s+организм", r"чувствительн\1 организм", s, flags=re.I)
    s = re.sub(r"хрупк(им|ой|ая|ую|ие|ого)\s+человек", r"уставш\1 человек", s, flags=re.I)
    s = re.sub(r"выглядишь\s+особенно\s+хрупкой", "выглядишь особенно уставшей", s, flags=re.I)
    s = re.sub(r"кажешься\s+такой\s+хрупкой", "кажешься такой уставшей", s, flags=re.I)
    s = re.sub(r"хрупкая,\s+с\s+испуг", "уставшая, с испуг", s, flags=re.I)
    s = re.sub(r"хрупкая,\s+доброй", "уставшая, доброй", s, flags=re.I)
    s = re.sub(r"хрупкой\s+малышки", "уставшей @", s, flags=re.I)
    s = re.sub(r"моей\s+хрупкой\s+жены", "моей уставшей жены", s, flags=re.I)
    s = re.sub(r"хрупкой\s+и\s+бледной", "уставшей и бледной", s, flags=re.I)
    s = re.sub(r"отважную\s+хрупкую", "отважную, но уставшую", s, flags=re.I)
    s = re.sub(r"хрупкая\s+и\s+нежная", "уставшая и нежная", s, flags=re.I)
    s = re.sub(r"хрупкая\s+и\s+светлая", "уставшая и светлая", s, flags=re.I)
    s = re.sub(r"хрупкая\s+и\s+тихая", "уставшая и тихая", s, flags=re.I)
    s = re.sub(r"хрупкая\s+и\s+упрямая", "уставшая и упрямая", s, flags=re.I)
    s = re.sub(r"хрупкая\s+и\s+нежная", "уставшая и нежная", s, flags=re.I)
    s = re.sub(r"хрупкая\s+девушка", "уставшая девушка", s, flags=re.I)
    s = re.sub(r"хрупк(ая|ой|ую|ие|им|ого)\b(?!\s+(организм|кож|цветок|нарцисс|кост|косточк))", r"уставш\1", s, flags=re.I)

    soften_control = (
        not allowed_romance
        or (hearts is not None and hearts < 6)
        or (allowed_romance and not severe)
    )
    if soften_control:
        s = s.replace("под моей защитой", "рядом со мной")
        s = s.replace("Под моей защитой", "Рядом со мной")
        s = s.replace("под моим строгим присмотром", "под моим наблюдением")
        s = s.replace("не отпущу тебя одну", "не оставлю тебя одну")
        s = s.replace("Не отпущу тебя", "Не оставлю тебя")
        s = s.replace("не отпущу тебя", "не оставлю тебя")
        s = s.replace("Я не отпущу", "Я не оставлю")
        s = s.replace("я не отпущу", "я не оставлю")
        s = s.replace("не отпущу твою руку", "не выпущу твою руку")
        s = s.replace("не отпущу ни на секунду", "не отойду ни на секунду")
        s = s.replace("никогда не отпущу тебя", "никогда не оставлю тебя")
        s = s.replace("не отпущу, пока", "не отойду, пока")
        s = s.replace("не позволю тебе", "не дам тебе")
        s = s.replace("Не позволю тебе", "Не дам тебе")
        s = s.replace("я не позволю", "я не дам")
        s = s.replace("Я не позволю", "Я не дам")
        s = s.replace("не позволю страху", "не дам страху")
        s = s.replace("не позволю стрессу", "не дам стрессу")
        s = s.replace("не позволю, чтобы", "не дам, чтобы")
        s = s.replace("не позволю никому", "не дам никому")
        s = s.replace("не позволю ничему", "не дам ничему")
        s = s.replace("не позволю ей", "не дам ей")
        s = s.replace("не позволю этому", "не дам этому")
        s = s.replace("не позволю никакой", "не дам никакой")
        s = s.replace("не позволю ни одному", "не дам ни одному")
        s = s.replace("не позволю солнцу", "не дам солнцу")
        s = s.replace("не позволю шторму", "не дам шторму")
        s = re.sub(r"не позволю\b(?![\w])", "не дам", s, flags=re.I)
        s = re.sub(r"не позволит\b", "не даст", s, flags=re.I)
        s = re.sub(r"не отпущу\b(?![\w])", "не отойду", s, flags=re.I)
    elif allowed_romance and severe:
        s = s.replace("под моей защитой", "рядом со мной — я не отступлю")
        s = s.replace("не отпущу тебя одну", "не оставлю тебя одну")
        s = s.replace("не отпущу тебя", "не оставлю тебя")
        s = s.replace("не позволю тебе", "не дам тебе")
        s = s.replace("Я не позволю", "Я не дам")

    s = re.sub(r"\bмоя\s+@\b", "@", s, flags=re.I)
    s = re.sub(r"\bмой\s+@\b", "@", s, flags=re.I)
    s = re.sub(r"уставшая и уставшая", "уставшая", s, flags=re.I)
    s = re.sub(r"твоей\s+хрупкости", "твоего состояния", s, flags=re.I)
    s = re.sub(r"Твоя\s+хрупкость", "Твоё состояние", s)
    s = re.sub(r"твоя\s+хрупкость", "твоё состояние", s, flags=re.I)
    s = re.sub(r"с\s+твоей\s+хрупкостью", "в твоём состоянии", s, flags=re.I)
    s = re.sub(r"организм\s+очень\s+хрупкий", "организм очень чувствительный", s, flags=re.I)
    s = re.sub(r"организм\s+слишком\s+хрупкий", "организм слишком чувствительный", s, flags=re.I)
    s = re.sub(r"хрупкому\s+сердцу", "чувствительному сердцу", s, flags=re.I)
    s = re.sub(r"несмотря\s+на\s+хрупкость", "несмотря на усталость", s, flags=re.I)
    s = re.sub(r"\bхрупкость\b", "усталость", s, flags=re.I)
    s = re.sub(r"\bхрупких\b", "уставших", s, flags=re.I)
    s = re.sub(r"организм\s+всё\s+ещё\s+хрупкий", "организм всё ещё чувствительный", s, flags=re.I)

    return s


def fix_ungated_base_strings(key: str, s: str) -> str:
    """Extra fixes for dialoguesHarvey ungated base (Вы, без ты/хрупкая)."""
    overrides = {
        "GreenRain": (
            "Сегодня необычная погода — зелёный дождь.$0#$b#Если почувствуете недомогание, "
            "приходите в клинику. Я буду на месте до конца дня.$a#$b#Не откладывайте обращение, "
            "если появятся головокружение или слабость.$0"
        ),
        "GreenRain_2": (
            "Я подготовил лёгкое успокоительное на случай дискомфорта от зелёного дождя.$h#$b#"
            "Если Вам станет тревожно — зайдите в клинику. Осмотр без записи.$0"
        ),
        "topicHarveyFirstVisitAgree": (
            "Вы согласились на домашний визит — это поможет составить план наблюдения.$h#$b#"
            "Я вижу признаки усталости и хочу, чтобы Вам было спокойно.$l#$b#"
            "Обсудим режим и лечение так, чтобы Вам было удобно. Я всё организую.$0"
        ),
        "topicHarveyFirstVisitRefused": (
            "Я слышу Вас и уважаю границы.$s#$b#Если станет тяжело или захочется поговорить — "
            "клиника открыта.$l#$b#Моя задача — быть рядом профессионально, без давления.$0"
        ),
        "topicHarveyFirstVisitNeutral": (
            "Понимаю, что перемены могут пугать.$s#$b#Не спешите — я рядом, когда будете готовы.$l#$b#"
            "Если захотите поговорить или просто посидеть в тишине — дверь клиники открыта.$0"
        ),
    }
    return overrides.get(key, s)


def parse_when_from_block(block: str) -> dict | None:
    m = re.search(r'"When"\s*:\s*\{([^}]+)\}', block, re.DOTALL)
    if not m:
        return None
    when = {}
    for km in re.finditer(r'"([^"]+)"\s*:\s*"([^"]*)"', m.group(1)):
        when[km.group(1)] = km.group(2)
    return when or None


def parse_target(block: str) -> str:
    m = re.search(r'"Target"\s*:\s*"([^"]+)"', block)
    return m.group(1) if m else ""


def parse_entries(block: str) -> tuple[int, int, dict] | None:
    m = re.search(r'"Entries"\s*:\s*\{', block)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(block)):
        if block[i] == "{":
            depth += 1
        elif block[i] == "}":
            depth -= 1
            if depth == 0:
                raw = block[start : i + 1]
                try:
                    return start, i + 1, json.loads(strip_comments(raw))
                except json.JSONDecodeError:
                    return None
    return None


def fmt_entries(entries: dict, indent: str = "        ") -> str:
    lines = []
    for k, v in entries.items():
        if isinstance(v, str):
            lines.append(f'{indent}"{k}": {json.dumps(v, ensure_ascii=False)},')
        else:
            lines.append(f'{indent}"{k}": {json.dumps(v, ensure_ascii=False)},')
    if lines:
        lines[-1] = lines[-1].rstrip(",")
    return "\n".join(lines)


def patch_file_fallback(text: str) -> tuple[str, int]:
    """Regex fallback for entries when block JSON parse fails."""
    count = 0

    def repl(m):
        nonlocal count
        key = m.group(1)
        val = m.group(2)
        new_val = fix_string(val, allowed_romance=False, severe=is_severe_medical(key, val), hearts=None)
        if new_val != val:
            count += 1
        return f'"{key}": {json.dumps(new_val, ensure_ascii=False)}'

    new_text = re.sub(
        r'"((?:HarveyMod_|mailHarvey)[^"]*)"\s*:\s*"((?:[^"\\]|\\.)*)"',
        repl,
        text,
    )
    return new_text, count


def patch_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    audit_rows: list[dict] = []
    fix_count = 0

    # split top-level Changes items crudely
    if '"Changes"' not in text:
        return audit_rows

    parts = re.split(r'(\n\s*\{\s*\n\s*"Action")', text)
    if len(parts) < 2:
        return audit_rows

    new_parts = [parts[0]]
    for i in range(1, len(parts), 2):
        prefix = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        block = prefix + body
        # only EditData blocks with Entries
        if '"Entries"' not in block:
            new_parts.append(block)
            continue

        target = parse_target(block)
        when = parse_when_from_block(block)
        allowed = is_allowed_romance(when, target)
        hm = hearts_max(when)

        ent = parse_entries(block)
        if not ent:
            new_parts.append(block)
            continue
        es, ee, entries = ent
        changed = False
        new_entries = {}
        for key, val in entries.items():
            if not isinstance(val, str):
                new_entries[key] = val
                continue
            orig = val
            new_val = val
            if not when and rel.endswith("dialoguesHarvey.json"):
                new_val = fix_ungated_base_strings(key, new_val)
            new_val = fix_string(
                new_val,
                allowed_romance=allowed,
                severe=is_severe_medical(key, new_val),
                hearts=hm,
            )
            new_entries[key] = new_val
            low = new_val.lower()
            matched = [p for p in PHRASES if p in low]
            if re.search(r"\b(моя|мой|моё|мое)\s+(девочка|храбрая|умница|жена|самая)", new_val, re.I):
                matched.append("моя/мой (romantic)")
            for phrase in matched:
                status, reason = classify(phrase, new_val, when, target, key)
                audit_rows.append({
                    "phrase": phrase,
                    "file": rel,
                    "key": key,
                    "gate": gate_label(when, target),
                    "action": status,
                    "reason": reason,
                    "changed": orig != new_val,
                })
            if new_val != orig:
                changed = True
                fix_count += 1

        if changed:
            new_block = block[:es] + "{\n" + fmt_entries(new_entries) + "\n      }" + block[ee:]
            new_parts.append(new_block)
        else:
            new_parts.append(block)

    new_text = "".join(new_parts)
    fb_count = 0
    if path.name == "mail.json":
        fb_text, fb_count = patch_file_fallback(new_text)
        new_text = fb_text
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    print(f"  {rel}: {fix_count + fb_count} values patched")
    return audit_rows


def classify(phrase: str, text: str, when: dict | None, target: str, key: str) -> tuple[str, str]:
    allowed = is_allowed_romance(when, target)
    hm = hearts_max(when)

    if phrase == "дорогая":
        if re.search(r"дорогая\s+стоимостью|мне\s+(?:очень\s+)?дорога|слишком\s+дорога", text, re.I):
            return "оставлено", "прилагательное «дорогая/дорога», не обращение"
        return "исправлено", "запрещено как pet name — солнышко/моя девочка"

    if phrase in ("солнышко", "малышка", "котёнок", "котенок", "девочка моя", "моя девочка", "любимая"):
        if allowed:
            return "оставлено", "Dating/Married/Pregnant gate"
        if hm and hm >= 6:
            return "исправлено", "Hearts 6–10 без Dating — заменено на @/нейтральное"
        return "исправлено", "нет gate Dating/Married"

    if phrase == "люблю":
        if allowed and re.search(r"люблю\s+тебя", text, re.I):
            return "оставлено", "Dating/Married — романтическое признание"
        if re.search(r"люблю\s+(такие|лес|когда|видеть|работать|готовить|читать|слушать|кофе|маринован)", text, re.I):
            return "оставлено", "не романтическое «люблю»"
        if re.search(r"люблю\s+тебя|моя\s+любовь", text, re.I):
            return "исправлено", "романтическое признание до Dating"
        return "review", "проверить контекст"

    if phrase == "хрупк":
        if allowed:
            return "оставлено", "Dating/Married — допустимо с осторожностью"
        if re.search(r"хрупк(им|ой|ая|ую|ие|ого)\s+(организм|кож|цветок|кост)", text, re.I):
            return "оставлено", "медицински нейтральный контекст"
        return "исправлено", "«хрупкая» о личности до Dating"

    if phrase in ("не отпущу", "не позволю", "под моей защитой"):
        if allowed and is_severe_medical(key, text):
            return "оставлено", "severe medical + Dating/Married — смягчённый вариант"
        if not when and not allowed:
            return "исправлено", "base без gate — смягчено"
        if allowed:
            return "исправлено", "Dating/Married без severe gate — смягчено"
        if hm and hm >= 6:
            return "исправлено", "6–10 pre-Dating — смягчено"
        return "исправлено", "до 6 ❤ или без gate — смягчено"

    if phrase == "моя/мой (romantic)":
        if allowed:
            return "оставлено", "Dating/Married"
        return "исправлено", "романтическое «моя/мой» до Dating"

    return "review", "—"


def scan_events(path: Path) -> list[dict]:
    rows = []
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    for m in re.finditer(r'speak\s+Harvey\s+"([^"]+)"', text):
        line = m.group(1)
        low = line.lower()
        for p in PHRASES:
            if p in low:
                rows.append({
                    "phrase": p,
                    "file": rel,
                    "key": "event dialogue",
                    "gate": "event script",
                    "action": "review",
                    "reason": "проверить условия события вручную",
                    "changed": False,
                })
    return rows


def main():
    total_patched = 0
    all_rows: list[dict] = []
    for path in sorted(ASSETS.glob("*.json")):
        if path.name in SKIP:
            continue
        print(f"Patching {path.name}...")
        rows = patch_file(path)
        all_rows.extend(rows)

    ev = ASSETS / "events.json"
    if ev.exists():
        all_rows.extend(scan_events(ev))

    # dedupe audit rows by file+key+phrase, prefer changed/fix
    seen = {}
    for r in all_rows:
        k = (r["file"], r["key"], r["phrase"])
        if k not in seen or r.get("changed"):
            seen[k] = r

    rows = list(seen.values())
    summary = defaultdict(int)
    for r in rows:
        summary[r["action"]] += 1

    lines = [
        "# Audit: pet names & forbidden tone (after fix)",
        "",
        "**Дата:** 2026-05-25  ",
        "**Скрипт:** `scripts/audit_pet_names.py`  ",
        "",
        "## Сводка",
        "",
        "| Статус | Кол-во |",
        "|--------|--------|",
    ]
    for st in ("оставлено", "исправлено", "review"):
        lines.append(f"| {st} | {summary.get(st, 0)} |")

    lines.extend([
        "",
        "## Таблица вхождений (после правки)",
        "",
        "| Фраза | Файл | Ключ/Event | Gate | Оставлено/исправлено | Причина |",
        "|-------|------|------------|------|----------------------|---------|",
    ])
    for r in sorted(rows, key=lambda x: (x["action"] != "исправлено", x["file"], x["phrase"], x["key"])):
        lines.append(
            f"| {r['phrase']} | {r['file']} | {r['key']} | {r['gate']} | {r['action']} | {r['reason']} |"
        )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
