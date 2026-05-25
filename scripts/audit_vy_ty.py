# -*- coding: utf-8 -*-
"""Audit/fix Harvey Вы/ты by relationship gate; write markdown report."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets" / "Code"
OUT = ROOT / "docs" / "audit-vy-ty-after-fix.md"

TARGET_GLOBS = (
    "dialoguesHarvey*.json",
    "events*.json",
    "mail*.json",
    "quest_dialogues.json",
)
SKIP = {"events_for_mode_new_formatted.json"}

TRUST_KEY_RE = re.compile(
    r"^(topicHarveyTrust_|topicHarveyStorm_|topicHarveyDoorSignal_|"
    r"topicHarveyBadDay_|topicHarveyHelp_|topicHarveyMines_|topicHarveySafetyKit_|"
    r"topicHarveyNotOnlyPatient|topicHarveyFuturePlan|HarveyOverhaul_E\d|"
    r"mailHarveyStorm_|topicHarveyWalk|topicHarveyDeclineFirstWalk|"
    r"topicHarveyAcceptFirstWalk|topicHarveyApology|topicHarveyQuietFiveMinutes|"
    r"topicHarveyNeedsSpace|topicHarveyWasCaredFor)",
    re.I,
)

TY_MARK = re.compile(
    r"\b(ты|тебя|тебе|тобой|твой|твоя|твоё|твои|твоей|твоему|твоим|твоих|твоими|твоём)\b",
    re.I,
)
VY_MARK = re.compile(
    r"\b(Вы|вы|Вас|вас|Вам|вам|Вами|вами|Ваш|ваш|Ваша|ваша|Ваше|ваше|Ваши|ваши|"
    r"Вашего|вашего|Вашей|вашей|Вашем|вашем|Вашим|вашим|Ваших|ваших)\b",
)

CYR = "а-яА-ЯёЁ"


def cyr_bound(word: str) -> str:
    w = re.escape(word)
    return rf"(?<![{CYR}]){w}(?![{CYR}])"


def apply_replacements(text: str, pairs: list[tuple[str, str]]) -> str:
    for pat, repl in pairs:
        if pat.startswith(r"\b") and pat.endswith(r"\b") and len(pat) > 4:
            word = pat[2:-2]
            pat = cyr_bound(word)
        text = re.sub(pat, repl, text)
    return text

# ty → Вы (order: longer / specific first)
TY_TO_VY: list[tuple[str, str]] = [
    (r"\bне стесняйся\b", "не стесняйтесь"),
    (r"\bНе стесняйся\b", "Не стесняйтесь"),
    (r"\bне пропускай\b", "не пропускайте"),
    (r"\bне рискуй\b", "не рискуйте"),
    (r"\bне бойся\b", "не бойтесь"),
    (r"\bНе бойся\b", "Не бойтесь"),
    (r"\bне обижайся\b", "не обижайтесь"),
    (r"\bне доводи\b", "не доводите"),
    (r"\bне игнорируй\b", "не игнорируйте"),
    (r"\bне спорь\b", "не спорьте"),
    (r"\bНе спорь\b", "Не спорьте"),
    (r"\bне перенапрягайся\b", "не перенапрягайтесь"),
    (r"\bне переутомляйся\b", "не переутомляйтесь"),
    (r"\bпообещай\b", "пообещайте"),
    (r"\bдоверься\b", "доверьтесь"),
    (r"\bобращайся\b", "обращайтесь"),
    (r"\bскажи\b", "скажите"),
    (r"\bСкажи\b", "Скажите"),
    (r"\bпокажи\b", "покажите"),
    (r"\bПокажи\b", "Покажите"),
    (r"\bприходи\b", "приходите"),
    (r"\bПриходи\b", "Приходите"),
    (r"\bдай\b", "дайте"),
    (r"\bДай\b", "Дайте"),
    (r"\bвозьми\b", "возьмите"),
    (r"\bВозьми\b", "Возьмите"),
    (r"\bнадень\b", "наденьте"),
    (r"\bНаден\b", "Наденьте"),
    (r"\bвыпей\b", "выпейте"),
    (r"\bне ешь\b", "не ешьте"),
    (r"\bне пренебрегай\b", "не пренебрегайте"),
    (r"\bслушай\b", "слушайте"),
    (r"\bСлушай\b", "Слушайте"),
    (r"\bдыши\b", "дышите"),
    (r"\bДыши\b", "Дышите"),
    (r"\bсадись\b", "садитесь"),
    (r"\bСадись\b", "Садитесь"),
    (r"\bбереги\b", "берегите"),
    (r"\bБереги\b", "Берегите"),
    (r"\bпозволь\b", "позвольте"),
    (r"\bПозволь\b", "Позвольте"),
    (r"\bсмотри\b", "смотрите"),
    (r"\bСмотри\b", "Смотрите"),
    (r"\bвыглядишь\b", "выглядите"),
    (r"\bчувствуешь\b", "чувствуете"),
    (r"\bЧувствуешь\b", "Чувствуете"),
    (r"\bзнаешь\b", "знаете"),
    (r"\bЗнаешь\b", "Знаете"),
    (r"\bможешь\b", "можете"),
    (r"\bМожешь\b", "Можете"),
    (r"\bхочешь\b", "хотите"),
    (r"\bХочешь\b", "Хотите"),
    (r"\bбудешь\b", "будете"),
    (r"\bБудешь\b", "Будете"),
    (r"\bпропускаешь\b", "пропускаете"),
    (r"\bвысыпаешься\b", "высыпаетесь"),
    (r"\bсобираешься\b", "собираетесь"),
    (r"\bСобираешься\b", "Собираетесь"),
    (r"\bнадеваешь\b", "надеваете"),
    (r"\bдержишь\b", "держите"),
    (r"\bпонимаешь\b", "понимаете"),
    (r"\bПонимаешь\b", "Понимаете"),
    (r"\bзамёрзла\b", "замёрзли"),
    (r"\bЗамёрзла\b", "Замёрзли"),
    (r"\bвыдержала\b", "выдержали"),
    (r"\bпростудилась\b", "простудились"),
    (r"\bпоранилась\b", "поранились"),
    (r"\bПоранилась\b", "Поранились"),
    (r"\bвыпила\b", "выпили"),
    (r"\bВыпила\b", "Выпили"),
    (r"\bплачешь\b", "плачете"),
    (r"\bПлачешь\b", "Плачете"),
    (r"\bустала\b", "устали"),
    (r"\bУстала\b", "Устали"),
    (r"\bготова\b", "готовы"),
    (r"\bуверена\b", "уверены"),
    (r"\bУверена\b", "Уверены"),
    (r"\bне забудь\b", "не забудьте"),
    (r"\bНе забудь\b", "Не забудьте"),
    (r"\bдержи\b", "держите"),
    (r"\bДержи\b", "Держите"),
    (r"\bне держи\b", "не держите"),
    (r"\bНе держи\b", "Не держите"),
    (r"\bЗайди\b", "Зайдите"),
    (r"\bзайди\b", "зайдите"),
    (r"\bСделаешь\b", "Сделаете"),
    (r"\bсделаешь\b", "сделаете"),
    (r"\bПоешь\b", "Поедите"),
    (r"\bпоешь\b", "поедите"),
    (r"\bПей\b", "Пейте"),
    (r"\bпей\b", "пейте"),
    (r"\bОтдохни\b", "Отдохните"),
    (r"\bотдохни\b", "отдохните"),
    (r"\bрасскажешь\b", "расскажете"),
    (r"\bРасскажешь\b", "Расскажете"),
    (r"\bОстанешься\b", "Останетесь"),
    (r"\bостанешься\b", "останетесь"),
    (r"\bпродолжай\b", "продолжайте"),
    (r"\bПродолжай\b", "Продолжайте"),
    (r"\bпочувствuешь\b", "почувствуете"),
    (r"\bПочувствuешь\b", "Почувствuете"),
    (r"\bкажешься\b", "кажетесь"),
    (r"\bКажешься\b", "Кажетесь"),
    (r"\bумеешь\b", "умеете"),
    (r"\bУмеешь\b", "Умеете"),
    (r"\bзаботишься\b", "заботитесь"),
    (r"\bЗаботишься\b", "Заботитесь"),
    (r"\bзамечаешь\b", "замечаете"),
    (r"\bЗамечаешь\b", "Замечаете"),
    (r"\bзахочешь\b", "захотите"),
    (r"\bЗахочешь\b", "Захотите"),
    (r"\bпредупреди\b", "предупредите"),
    (r"\bПредупреди\b", "Предупредите"),
    (r"\bрасскажи\b", "расскажите"),
    (r"\bРасскажи\b", "Расскажите"),
    (r"\bделаешь\b", "делаете"),
    (r"\bДелаешь\b", "Делаете"),
    (r"\bмолчишь\b", "молчите"),
    (r"\bМолчишь\b", "Молчите"),
    (r"\bпрячешься\b", "прячетесь"),
    (r"\bПрячешься\b", "Прячетесь"),
    (r"\bСядь\b", "Сядьте"),
    (r"\bсядь\b", "сядьте"),
    (r"\bСледи\b", "Следите"),
    (r"\bследи\b", "следите"),
    (r"\bДелай\b", "Делайте"),
    (r"\bделай\b", "делайте"),
    (r"\bЛожись\b", "Ложитесь"),
    (r"\bложись\b", "ложитесь"),
    (r"\bИди\b", "Идите"),
    (r"\bиди\b", "идите"),
    (r"\bПоговори\b", "Поговорите"),
    (r"\bпоговори\b", "поговорите"),
    (r"\bОставайся\b", "Оставайтесь"),
    (r"\bоставайся\b", "оставайтесь"),
    (r"\bНачинай\b", "Начинайте"),
    (r"\bначинай\b", "начинайте"),
    (r"\bНе торопись\b", "Не торопитесь"),
    (r"\bне торопись\b", "не торопитесь"),
    (r"\bСделай\b", "Сделайте"),
    (r"\bсделай\b", "сделайте"),
    (r"\bПосмотри\b", "Посмотрите"),
    (r"\bпосмотри\b", "посмотрите"),
    (r"\bПопробуй\b", "Попробуйте"),
    (r"\bпопробуй\b", "попробуйте"),
    (r"\bПобудь\b", "Побудьте"),
    (r"\bпобудь\b", "побудьте"),
    (r"\bОтдыхай\b", "Отдыхайте"),
    (r"\bотдыхай\b", "отдыхайте"),
    (r"\bДышите\b", "Дышите"),  # noop anchor
    (r"\bстараешься\b", "стараетесь"),
    (r"\bСтараешься\b", "Стараетесь"),
    (r"\bнапрягаешься\b", "напрягаетесь"),
    (r"\bпереживаешь\b", "переживаете"),
    (r"\bПереживаешь\b", "Переживаете"),
    (r"\bдумаешь\b", "думаете"),
    (r"\bДумаешь\b", "Думаете"),
    (r"\bрискуешь\b", "рискуете"),
    (r"\bРискuешь\b", "Рискuете"),
    (r"\bдрожишь\b", "дрожите"),
    (r"\bДрожишь\b", "Дрожите"),
    (r"\bнадела\b", "надели"),
    (r"\bвзяла\b", "взяли"),
    (r"\bВзяла\b", "Взяли"),
    (r"\bспала\b", "спали"),
    (r"\bСпала\b", "Спали"),
    (r"\bела\b", "ели"),
    (r"\bЕла\b", "Ели"),
    (r"\bвыходишь\b", "выходите"),
    (r"\bВыходишь\b", "Выходите"),
    (r"\bпредставляешь\b", "представляете"),
    (r"\bзапираешься\b", "запираетесь"),
    (r"\bприняла\b", "приняли"),
    (r"\bПриняла\b", "Приняли"),
    (r"\bпровела\b", "провели"),
    (r"\bПровела\b", "Провели"),
    (r"\bсправишься\b", "справитесь"),
    (r"\bСправишься\b", "Справитесь"),
    (r"\bпосетила\b", "посетили"),
    (r"\bПосетила\b", "Посетили"),
    (r"\bВидишь\b", "Видите"),
    (r"\bвидишь\b", "видите"),
    (r"\bидёшь\b", "идёте"),
    (r"\bИдёшь\b", "Идёте"),
    (r"\bвспомни\b", "вспомните"),
    (r"\bВспомни\b", "Вспомните"),
    (r"\bсправилась\b", "справились"),
    (r"\bСправилась\b", "Справились"),
    (r"\bпреодолела\b", "преодолели"),
    (r"\bуверена\b", "уверены"),
    (r"\bувходишь\b", "уходите"),
    (r"\bУходишь\b", "Уходите"),
    (r"\bчувствуешь\b", "чувствуете"),
    (r"\bЧувствuешь\b", "Чувствuете"),
    (r"\bверишь\b", "верите"),
    (r"\bВеришь\b", "Верите"),
    (r"\bулыбнуться\b", "улыбнуться"),  # infinitive noop
    (r"\bпочувствуешь\b", "почувствuете"),
    (r"\bПочувствuешь\b", "Почувствuете"),
    (r"\bладишь\b", "ладите"),
    (r"\bЛadишь\b", "Ладите"),
    (r"\bсоздаёшь\b", "создаёте"),
    (r"\bСоздаёшь\b", "Создаёте"),
    (r"\bобязана\b", "обязаны"),
    (r"\bОбязана\b", "Обязаны"),
    (r"\bтвоём\b", "Вашем"),
    (r"\bтвоем\b", "Вашем"),
    (r"\bтвоей\b", "Вашей"),
    (r"\bтвоего\b", "Вашего"),
    (r"\bтвоим\b", "Вашим"),
    (r"\bтвоих\b", "Ваших"),
    (r"\bтвоими\b", "Вашими"),
    (r"\bтвоему\b", "Вашему"),
    (r"\bтебя\b", "Вас"),
    (r"\bТебя\b", "Вас"),
    (r"\bтебе\b", "Вам"),
    (r"\bТебе\b", "Вам"),
    (r"\bтобой\b", "Вами"),
    (r"\bТобой\b", "Вами"),
    (r"\bтвой\b", "Ваш"),
    (r"\bТвой\b", "Ваш"),
    (r"\bтвоя\b", "Ваша"),
    (r"\bТвоя\b", "Ваша"),
    (r"\bтвоё\b", "Ваше"),
    (r"\bТвоё\b", "Ваше"),
    (r"\bтвое\b", "Ваше"),
    (r"\bтвои\b", "Ваши"),
    (r"\bТвои\b", "Ваши"),
    (r"\bты\b", "Вы"),
    (r"\bТы\b", "Вы"),
]

VY_TO_TY: list[tuple[str, str]] = [
    (r"\bне стесняйтесь\b", "не стесняйся"),
    (r"\bНе стесняйтесь\b", "Не стесняйся"),
    (r"\bне пропускайте\b", "не пропускай"),
    (r"\bне рискуйте\b", "не рискуй"),
    (r"\bне бойтесь\b", "не бойся"),
    (r"\bНе бойтесь\b", "Не бойся"),
    (r"\bприходите\b", "приходи"),
    (r"\bПриходите\b", "Приходи"),
    (r"\bПожалуйста, приходите\b", "Пожалуйста, приходи"),
    (r"\bскажите\b", "скажи"),
    (r"\bСкажите\b", "Скажи"),
    (r"\bпокажите\b", "покажи"),
    (r"\bПокажите\b", "Покажи"),
    (r"\bдайте\b", "дай"),
    (r"\bДайте\b", "Дай"),
    (r"\bвозьмите\b", "возьми"),
    (r"\bВозьмите\b", "Возьми"),
    (r"\bвыглядите\b", "выглядишь"),
    (r"\bчувствуете\b", "чувствуешь"),
    (r"\bзнаете\b", "знаешь"),
    (r"\bможете\b", "можешь"),
    (r"\bхотите\b", "хочешь"),
    (r"\bбудете\b", "будешь"),
    (r"\bпропускаете\b", "пропускаешь"),
    (r"\bвысыпаетесь\b", "высыпаешься"),
    (r"\bсобираетесь\b", "собираешься"),
    (r"\bВашем\b", "твоём"),
    (r"\bвашем\b", "твоём"),
    (r"\bВашей\b", "твоей"),
    (r"\bвашей\b", "твоей"),
    (r"\bВашего\b", "твоего"),
    (r"\bвашего\b", "твоего"),
    (r"\bВашим\b", "твоим"),
    (r"\bвашим\b", "твоим"),
    (r"\bВаших\b", "твоих"),
    (r"\bваших\b", "твоих"),
    (r"\bВашими\b", "твоими"),
    (r"\bвашими\b", "твоими"),
    (r"\bВашему\b", "твоему"),
    (r"\bвашему\b", "твоему"),
    (r"\bВас\b", "тебя"),
    (r"\bвас\b", "тебя"),
    (r"\bВам\b", "тебе"),
    (r"\bвам\b", "тебе"),
    (r"\bВами\b", "тобой"),
    (r"\bвами\b", "тобой"),
    (r"\bВаш\b", "твой"),
    (r"\bваш\b", "твой"),
    (r"\bВаша\b", "твоя"),
    (r"\bваша\b", "твоя"),
    (r"\bВаше\b", "твоё"),
    (r"\bваше\b", "твоё"),
    (r"\bВаши\b", "твои"),
    (r"\bваши\b", "твои"),
    (r"\bВы\b", "ты"),
    (r"\bвы\b", "ты"),
]


def strip_comments(text: str) -> str:
    return re.sub(r"^\s*//.*$", "", text, flags=re.MULTILINE)


def gate_label(when: dict | None, target: str = "") -> str:
    if when:
        return "; ".join(f"{k}={v}" for k, v in when.items())
    if "MarriageDialogue" in target:
        return "MarriageDialogue (Married)"
    return "ungated"


def hearts_range(when: dict | None) -> tuple[int | None, int | None]:
    if not when:
        return None, None
    h = when.get("Hearts:Harvey", "")
    nums = [int(x) for x in h.split(",") if x.strip().isdigit()]
    if not nums:
        return None, None
    return min(nums), max(nums)


def friendship_min(when: dict | None) -> int | None:
    if not when:
        return None
    for k, v in when.items():
        if "Friendship" in k and "Harvey" in k:
            m = re.search(r"(\d+)", v)
            if m:
                return int(m.group(1))
    return None


def is_trust_exception(key: str) -> bool:
    return bool(TRUST_KEY_RE.search(key))


def expected_mode(when: dict | None, key: str, target: str) -> str:
    """vy | ty | exception"""
    if is_trust_exception(key):
        return "exception"
    if when:
        rel = when.get("Relationship:Harvey", "")
        if rel in ("Dating", "Married"):
            return "ty"
        if any(k.startswith("Pregnant") for k in when):
            return "ty"
    if "MarriageDialogue" in target:
        return "ty"
    hmin, hmax = hearts_range(when)
    if hmax is not None and hmax <= 2:
        return "vy"
    if hmin is not None and hmin >= 3:
        return "ty"
    fp = friendship_min(when)
    if fp is not None:
        return "ty" if fp >= 750 else "vy"
    # ungated fallback = stage 0
    return "vy"


def detect_mode(text: str) -> str:
    has_ty = bool(TY_MARK.search(text))
    has_vy = bool(VY_MARK.search(text))
    if has_ty and has_vy:
        return "mixed"
    if has_ty:
        return "ty"
    if has_vy:
        return "vy"
    return "neutral"


def to_vy(text: str) -> str:
    return apply_replacements(text, TY_TO_VY)


def to_ty(text: str) -> str:
    return apply_replacements(text, VY_TO_TY)


def fix_text(text: str, mode: str) -> str:
    if mode == "vy":
        return to_vy(text)
    if mode == "ty":
        return to_ty(text)
    return text


def parse_when(block: str) -> dict | None:
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


def summarize_formality(text: str) -> str:
    m = detect_mode(text)
    if m == "mixed":
        return "смешанное"
    if m == "ty":
        return "ты"
    if m == "vy":
        return "Вы"
    return "нейтральное"


def patch_json_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    rows: list[dict] = []
    if '"Changes"' not in text:
        return rows

    parts = re.split(r'(\n\s*\{\s*\n\s*"Action")', text)
    new_parts = [parts[0]]
    fix_count = 0

    for i in range(1, len(parts), 2):
        block = parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
        if '"Entries"' not in block:
            new_parts.append(block)
            continue
        target = parse_target(block)
        when = parse_when(block)
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
            exp = expected_mode(when, key, target)
            if exp == "exception":
                new_entries[key] = val
                if TY_MARK.search(val) or VY_MARK.search(val):
                    rows.append({
                        "file": rel, "key": key, "gate": gate_label(when, target),
                        "was": summarize_formality(val), "now": summarize_formality(val),
                        "comment": "trust-arc exception — без правки",
                    })
                continue
            cur = detect_mode(val)
            if exp == "vy":
                fixed = to_vy(val)
            elif exp == "ty" and cur in ("vy", "mixed"):
                fixed = to_ty(val)
            else:
                new_entries[key] = val
                continue
            if fixed != val:
                fix_count += 1
                changed = True
                rows.append({
                    "file": rel, "key": key, "gate": gate_label(when, target),
                    "was": summarize_formality(val), "now": summarize_formality(fixed),
                    "comment": f"исправлено: {cur} → {exp} по gate",
                })
            new_entries[key] = fixed

        if changed:
            block = block[:es] + "{\n" + fmt_entries(new_entries) + "\n      }" + block[ee:]
        new_parts.append(block)

    new_text = "".join(new_parts)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    print(f"  {rel}: {fix_count} keys")
    return rows


def patch_events_file(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    rows: list[dict] = []

    # event keys: "eventId/conditions...": "script..."
    for m in re.finditer(r'"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', text):
        ekey, script = m.group(1), m.group(2)
        if "Harvey" not in script and "harvey" not in script.lower():
            continue
        gate = "ungated"
        if "Friendship Harvey" in ekey or "friendship Harvey" in ekey:
            fm = re.search(r"Friendship\s+Harvey\s+(\d+)", ekey)
            if fm:
                gate = f"Friendship:Harvey>={fm.group(1)}"
        if "Relationship:Harvey" in ekey or "Dating" in ekey or "Married" in ekey:
            gate = "Relationship gate in event id"
        if is_trust_exception(ekey) or "HarveyOverhaulStory" in ekey or "HarveyOverhaul_E" in ekey:
            if TY_MARK.search(script) or VY_MARK.search(script):
                rows.append({
                    "file": rel, "key": ekey[:80], "gate": gate,
                    "was": summarize_formality(script), "now": summarize_formality(script),
                    "comment": "trust/story event — без автоправки",
                })
            continue
        exp = "ty" if ("Dating" in ekey or "Married" in ekey or re.search(r"Friendship\s+Harvey\s+(\d+)", ekey) and int(re.search(r"Friendship\s+Harvey\s+(\d+)", ekey).group(1)) >= 750) else "vy"
        cur = detect_mode(script)
        if cur in ("neutral", exp) or cur == "mixed":
            continue
        if cur != exp:
            fixed = fix_text(script, exp)
            if fixed != script:
                text = text.replace(f'"{ekey}": "{script}"', f'"{ekey}": {json.dumps(fixed, ensure_ascii=False)}', 1)
                rows.append({
                    "file": rel, "key": ekey[:80], "gate": gate,
                    "was": summarize_formality(script), "now": summarize_formality(fixed),
                    "comment": f"event speak: {cur} → {exp}",
                })

    if text != path.read_text(encoding="utf-8"):
        path.write_text(text, encoding="utf-8")
    return rows


def main():
    all_rows: list[dict] = []
    files = []
    for pat in TARGET_GLOBS:
        files.extend(ASSETS.glob(pat))
    files = sorted({p for p in files if p.name not in SKIP})

    for path in files:
        print(f"Patching {path.name}...")
        if path.name.startswith("events"):
            all_rows.extend(patch_events_file(path))
        else:
            all_rows.extend(patch_json_file(path))

    exceptions = [r for r in all_rows if "exception" in r["comment"] or "trust" in r["comment"]]
    fixes = [r for r in all_rows if r["was"] != r["now"]]

    lines = [
        "# Audit: обращение Вы/ты (after fix)",
        "",
        "**Дата:** 2026-05-25  ",
        "**Скрипт:** `scripts/audit_vy_ty.py`  ",
        "**C# messages:** в репозитории `[CP]` не найдены (только Content Patcher JSON).",
        "",
        "## Сводка",
        "",
        f"- **Исправлено ключей/событий:** {len(fixes)}",
        f"- **Trust-arc exceptions (без правки):** {len(exceptions)}",
        "",
        "### Осознанные исключения (trust-arc, «Вы» сохранено)",
        "",
        "| Паттерн ключей | Причина |",
        "|----------------|---------|",
        "| `topicHarveyTrust_*` | Event-gated trust arc — границы и согласие |",
        "| `topicHarveyStorm_*`, `topicHarveyDoorSignal_*` | Storm/safety trust protocol |",
        "| `topicHarveyBadDay_*`, `topicHarveyHelp_*`, `topicHarveyMines_*` | Post-event trust topics |",
        "| `topicHarveyWalk*`, `topicHarveyApology*`, `topicHarveyNeedsSpace` | First walk / opt-out arc |",
        "| `HarveyOverhaul_E*`, `HarveyOverhaulStory.E*` | Story mail/events ladder 0→2b |",
        "| `mailHarveyStorm_*` | Storm trust mail |",
        "",
        "## Таблица правок",
        "",
        "| Файл | Ключ/Event | Gate | Было | Стало | Комментарий |",
        "|------|------------|------|------|-------|-------------|",
    ]
    for r in fixes:
        lines.append(
            f"| {r['file']} | {r['key']} | {r['gate']} | {r['was']} | {r['now']} | {r['comment']} |"
        )
    if not fixes:
        lines.append("| — | — | — | — | — | явных нарушений не осталось |")

    lines.extend([
        "",
        "## Trust-arc (оставлено без правки)",
        "",
        "| Файл | Ключ/Event | Gate | Обращение | Комментарий |",
        "|------|------------|------|-----------|-------------|",
    ])
    seen = set()
    for r in exceptions:
        k = (r["file"], r["key"])
        if k in seen:
            continue
        seen.add(k)
        lines.append(
            f"| {r['file']} | {r['key']} | {r['gate']} | {r['was']} | {r['comment']} |"
        )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(fixes)} fixes, {len(exceptions)} exceptions)")


if __name__ == "__main__":
    main()
