# -*- coding: utf-8 -*-
"""Patch dialoguesHarveyCure.json tone layers in-place."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "assets/Code/dialoguesHarveyCure.json"

FORBIDDEN_VOUS = (
    "солнышко", "малышка", "котёнок", "котенок", "девочка моя", "любимая",
    "не отпущу", "не позволю", "под моей защитой", "хрупкая", "хрупкий",
    "хрупкую", "хрупкой", "хрупкие", "хрупким",
)
FORBIDDEN_PRE_DATING = FORBIDDEN_VOUS + ("моя хорошая", "не отпускает", "не отпускаю")


def find_hearts_blocks(text):
    blocks = []
    for m in re.finditer(r'"Hearts:Harvey":\s*"([^"]+)"', text):
        when = m.group(1)
        block_start = text.rfind("{", 0, m.start())
        block_end = text.find("\n        },", m.start())
        if block_end == -1:
            block_end = len(text)
        else:
            block_end += len("\n        },")
        blocks.append((when, block_start, block_end))
    return blocks


def get_entries_bounds(text, block_start, block_end):
    chunk = text[block_start:block_end]
    m = re.search(r'"Entries":\s*\{', chunk)
    if not m:
        return None
    abs_start = block_start + m.end()
    depth = 1
    i = abs_start
    while i < block_end and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return abs_start, i


def iter_entry_matches(text, es, ee):
    for m in re.finditer(r'"([^"]+)":\s*"((?:[^"\\]|\\.)*)"', text[es:ee]):
        yield m.group(1), m.group(2), es + m.start(), es + m.end()


def set_entry(text, start, end, key, value):
    esc = value.replace("\\", "\\\\").replace('"', '\\"')
    return text[:start] + f'"{key}": "{esc}"' + text[end:]


def insert_entries(text, insert_at, entries):
    lines = []
    for k, v in entries.items():
        esc = v.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'                "{k}": "{esc}",')
    blob = "\n" + "\n".join(lines)
    return text[:insert_at] + blob + text[insert_at:]


def to_vous(text):
    if any(w in text.lower() for w in FORBIDDEN_VOUS):
        text = re.sub(r"(?i)не позволю[^.!?$]*", "недопустимо", text)
        text = re.sub(r"(?i)не отпущу[^.!?$]*", "не оставлю без наблюдения", text)
        text = re.sub(r"(?i)под моей защитой", "под медицинским наблюдением", text)
        text = re.sub(r"(?i)хрупк[а-яё]+", "ослабленная", text)
    pairs = [
        (r"\bслушалась\b", "слушались"), (r"\bсправилась\b", "справились"),
        (r"\bвыдержала\b", "выдержали"), (r"\bвыздоровела\b", "выздоровели"),
        (r"\bодна\b", "в одиночку"), (r"\bодной\b", "в одиночку"),
        (r"на тебя", "на Вас"), (r"с тобой", "с Вами"), (r"за тобой", "за Вами"),
        (r"к тебе", "к Вам"), (r"тебя", "Вас"), (r"тебе", "Вам"), (r"тобой", "Вами"),
        (r"твоими", "Вашими"), (r"твоих", "Ваших"), (r"твоему", "Вашему"),
        (r"твоей", "Вашей"), (r"твоё", "Ваше"), (r"твою", "Вашу"), (r"твои", "Ваши"),
        (r"твой", "Ваш"), (r"твоя", "Ваша"),
        (r"почувствуешь", "почувствуете"), (r"остановись", "остановитесь"),
        (r"будь ", "будьте "), (r"держи", "держите"), (r"не мочи", "не мочите"),
        (r"не трогай", "не трогайте"), (r"не спорь", "не спорьте"),
        (r"не рискуй", "не рискуйте"), (r"не бегай", "не бегайте"),
        (r"сообщи", "сообщите"), (r"скажи", "скажите"), (r"приходи", "приходите"),
        (r"покажи", "покажите"), (r"расскажи", "расскажите"),
        (r"дыши", "дышите"), (r"терпи", "терпите"), (r"смотри", "смотрите"),
        (r"слушай", "слушайтесь"), (r"встань", "встаньте"), (r"коснись", "коснитесь"),
        (r"назови", "назовите"), (r"работай", "работайте"), (r"отдыхай", "отдыхайте"),
        (r"молодец, что пришла", "Хорошо, что пришли"),
        (r"отпущу", "отпущу после осмотра"), (r"\bты\b", "Вы"),
    ]
    for a, b in pairs:
        text = re.sub(a, b, text, flags=re.IGNORECASE)
    return text


def strip_forbidden(text, pre_dating=False):
    forbidden = FORBIDDEN_PRE_DATING if pre_dating else FORBIDDEN_VOUS
    for w in forbidden:
        text = re.sub(re.escape(w), "", text, flags=re.IGNORECASE)
    return re.sub(r"\s{2,}", " ", text).strip()


def stage1(text):
    text = strip_forbidden(text)
    return text.replace("не спорь со мной", "давай без споров").replace("Не спорь", "Давай без споров")


def stage2(text):
    text = strip_forbidden(text, pre_dating=True)
    text = re.sub(r"(?i)не отпускает[^%]*", "", text)
    text = re.sub(r"(?i)не позволю[^!?$]*", "режим соблюдаем", text)
    text = re.sub(r"(?i)не отпущу[^!?$]*", "я прослежу", text)
    return text


def vous_to_ty(text):
    text = text.replace("Вас", "тебя").replace("Вам", "тебе").replace("Вами", "тобой")
    text = text.replace("Ваш", "твой").replace("Ваше", "твоё").replace("Ваша", "твоя")
    text = text.replace("Ваши", "твои").replace("Вашу", "твою").replace("Вашей", "твоей")
    text = re.sub(r"\bВы\b", "ты", text)
    text = text.replace("Остаётесь", "Остаёшься").replace("Работайте", "Работай")
    text = text.replace("Соблюдайте", "Соблюдай").replace("пришли", "пришла")
    text = text.replace("выдержали", "выдержала").replace("справились", "справилась")
    return text


def fix_vous_key(key, val):
    v = to_vous(val)
    if key.startswith("Treat_") and "_Before" in key:
        if re.search(r"\b(ты|тебя|тебе|тво|Покажи|Сядь|Стоп|Дай|Потерпи)\b", v, re.I):
            v = "Сейчас осмотрю и обработаю.$0#$b#Покажите, где болит — начну по протоколу.$0"
    elif key.startswith("Treat_") and "_After" in key:
        if re.search(r"\b(ты|тебя|тебе|тво|Меняй|Двигай|Сохраняй|Слушай)\b", v, re.I):
            v = "После перевязки избегайте нагрузки.$0#$b#Если боль усилится — сразу приходите в клинику.$a"
    elif key.startswith("Recovery_Complete"):
        v = strip_forbidden(to_vous(v))
    elif key.startswith("Proximity_"):
        v = to_vous(val).replace("держись", "постарайтесь не двигаться")
    elif key == "topicHarvey_NightRound":
        v = "%Харви тихо входит.#$b#Проверю показатели. Если разбужу — это по протоколу.$0#%Он аккуратно проверяет состояние."
    elif "Phase" in key or key.startswith("Treatment_Phase"):
        v = to_vous(val)
    return v


CURED_3_5 = {
    "topicHurtCured": "%Харви снимает повязку.#$b#Заживление хорошее. Давай проверим — мне важно, чтобы заживление шло нормально. Работай в перчатках.$0#%Он напоминает о профилактике.",
    "topicBadlyHurtCured": "%Харви проверяет место травмы.#$b#Зажило. Сегодня без тяжёлой работы, хорошо? При боли — сразу в клинику.$0#%Он даёт рекомендации.",
    "topicBruisedRibsCured": "%Харви слушает твоё дыхание.#$b#Ушиб зажил. Тяжести ещё неделю без — договорились?$0#%Он даёт рекомендации.",
    "topicSprainedAnkleCured": "%Харви проверяет лодыжку.#$b#Растяжение прошло. Не бегай по лесу в одиночку — завтра на повторный осмотр.$0#%Он напоминает об осторожности.",
    "topicBackStrainCured": "%Харви проверяет спину.#$b#Спазм прошёл. Делай перерывы — сегодня без тяжёлой работы, хорошо?$0#%Он даёт советы по профилактике.",
    "topicDeepCutsCured": "%Харви осматривает зажившие раны.#$b#Порезы затянулись. Будь осторожнее с острыми предметами — если что-то не так, сразу ко мне.$0#%Он напоминает о безопасности.",
    "topicBurnWoundsCured": "%Харви осматривает руки.#$b#Ожоги прошли. Береги руки у огня — при покраснении сразу приходи.$0#%Он даёт советы по уходу.",
    "topicConcussionCured": "%Харви проверяет зрачки.#$b#Сотрясение прошло. Полный покой соблюдала — спасибо. Без опасных высот ещё несколько дней.$0#%Он напоминает о режиме.",
    "topicFracturedBoneCured": "%Харви изучает рентген.#$b#Кость срослась — гипс снимаем. Нагрузки возвращай постепенно, без шахты.$0#%Он назначает реабилитацию.",
    "topicInfectedWoundCured": "%Харви проверяет анализы.#$b#Инфекция ушла. Курс доведи до конца — при температуре сразу ко мне.$0#%Он напоминает о профилактике.",
    "topicColdCured": "%Харви проверяет температуру.#$b#Простуда прошла. Одевайся теплее — не хочу повторения.$0#%Он напоминает о профилактике.",
    "topicSurgicalWoundCured": "%Харви осматривает шов.#$b#Зажило хорошо. Возвращай активность постепенно — без резких нагрузок.$0#%Он даёт рекомендации.",
    "topicHarvey_NightRound": "%Харви тихо входит.#$b#Проверю показатели. Не спи слишком глубоко — если что-то не так, скажи.$0#%Он аккуратно проверяет состояние.",
    "topicStartTreatment": "%Харви осматривает тебя.#$b#Вижу, что нужна помощь. Сейчас проведу осмотр и назначу лечение.$0#%Он готовит инструменты.",
    "topicHarvey_EscalatedCare": "%Харви серьёзно смотрит на тебя.#$b#Состояние требует более интенсивного лечения. Остаёшься под наблюдением до стабилизации.$a#%Он готовит оборудование.",
}

CURED_6_10 = {
    "topicHurtCured": "%Харви снимает повязку.#$b#Рана затянулась. Ты снова решила справиться одна? Я помогу, но больше не тяни до такого состояния.$a#$b#Если заболит — сразу ко мне.$0#%Он смотрит строго, но с заботой.",
    "topicBadlyHurtCured": "%Харви проверяет место травмы.#$b#Зажило. Я рядом — но мне нужно, чтобы ты больше не рисковала так. При слабости — сразу в клинику.$a#%Он не отводит взгляд, пока не убедится, что ты поняла.",
    "topicBruisedRibsCured": "%Харви слушает дыхание.#$b#Ушиб зажил. Я не хочу снова видеть эту боль хуже. Никаких тяжестей ещё неделю.$a#%Он даёт чёткие инструкции.",
    "topicSprainedAnkleCured": "%Харви проверяет лодыжку.#$b#Растяжение прошло. Не бегай одна по лесу — я серьёзно. При малейшей боли — остановись и скажи мне.$a#%Он настойчиво напоминает о режиме.",
    "topicBackStrainCured": "%Харви проверяет спину.#$b#Спазм прошёл. Перерывы обязательны — знаю, как ты работаешь, но сегодня без тяжёлого.$a#$b#%Он даёт советы по профилактике.",
    "topicDeepCutsCured": "%Харви осматривает рубцы.#$b#Порезы затянулись. Будь осторожнее с острыми предметами — одна ты мне здесь не нужна в таком виде.$a#%Он подробно объясняет уход.",
    "topicBurnWoundsCured": "%Харви осматривает руки.#$b#Ожоги прошли. Береги руки у огня — при покраснении сразу ко мне.$a#%Он даёт советы по уходу.",
    "topicTornMusclesCured": "%Харви проверяет силу рук.#$b#Мышцы восстановились. Разминку не пропускай — переутомление снова недопустимо.$a#%Он даёт рекомендации по нагрузке.",
    "topicConcussionCured": "%Харви проверяет зрачки.#$b#Сотрясение прошло. Сейчас я врач — спорить будем после осмотра. Без высоты и резких движений.$a#%Он напоминает о безопасности.",
    "topicFracturedBoneCured": "%Харви изучает рентген.#$b#Кость срослась. Нагрузки постепенно — я прослежу. При боли — сразу сообщи.$a#%Он даёт план реабилитации.",
    "topicShrapnelWoundsCured": "%Харви осматривает шрамы.#$b#Осколочные раны зажили. Держись подальше от опасных мест — при боли сразу ко мне.$a#%Он напоминает о безопасности.",
    "topicInfectedWoundCured": "%Харви проверяет анализы.#$b#Инфекция ушла. Я рядом — но курс AB доведи до конца. Температура — сразу ко мне.$0#%Он напоминает о профилактике.",
    "topicColdCured": "%Харви проверяет температуру.#$b#Простуда прошла. Одевайся теплее — не хочу снова видеть тебя больной.$a#%Он напоминает о профилактике.",
    "topicSurgicalWoundCured": "%Харви осматривает шов.#$b#Зажило хорошо. Возвращай активность постепенно — я прослежу за нагрузкой.$0#%Он даёт рекомендации.",
    "topicHarvey_NightRound": "%Харви тихо входит.#$b#Проверю показатели. Я рядом — просто дай мне спокойно всё проверить.$0#%Он аккуратно проверяет состояние.",
    "topicStartTreatment": "%Харви быстро оценивает состояние.#$b#Ты снова решила справиться одна? Рассказывай, что случилось — мне нужна полная картина.$a#%Он готовит инструменты.",
    "topicHarvey_EscalatedCare": "%Харви изучает карту пациента.#$b#Мне не нравится, как часто ты здесь с травмами. С завтрашнего дня — более строгое наблюдение.$a#%Он говорит серьёзно о безопасности.",
    "Treat_Hurt_Before1": "Ты опять терпела до последнего?$8#$b#Покажи, где болит. Я рядом — сейчас осмотрю и обработаю.$0",
    "Treat_Hurt_After1": "Повязка на месте.$0#$b#После перевязки — без нагрузки. Если боль усилится — сразу в клинику, не тяни.$a",
}

PROX_VOUS = {
    "Proximity_DirtyWound": "Рана загрязнилась.$a#$b#Сейчас промою и обработаю по протоколу.$a",
    "Proximity_WetBandage": "Повязка промокла.$s#$b#Меняю немедленно — риск инфекции.$0",
    "Proximity_WetStitches": "Швы намокли.$a#$b#Обработаю антисептиком, наложу водостойкую повязку.$0",
    "Proximity_AllergicRash": "Аллергическая реакция.$u#$b#Отменяю препарат, подберу замену.$0",
    "Proximity_PainFlare": "Боль усилилась?$s#$b#Дам обезболивающее. Если не поможет или появится жар — осмотр в клинике.$u",
}


def patch_block(text, when, transform_fn, overrides=None):
    blocks = find_hearts_blocks(text)
    target = next((b for b in blocks if b[0] == when), None)
    if not target:
        return text, {}
    _, bs, be = target
    bounds = get_entries_bounds(text, bs, be)
    if not bounds:
        return text, {}
    es, ee = bounds
    entries = {}
    patches = []
    for key, val, s, e in iter_entry_matches(text, es, ee):
        entries[key] = val
        new_val = overrides.get(key, transform_fn(key, val)) if overrides and key in overrides else transform_fn(key, val)
        if new_val != val:
            patches.append((s, e, key, new_val))
    for s, e, key, new_val in reversed(patches):
        text = set_entry(text, s, e, key, new_val)
        entries[key] = new_val
    if overrides:
        existing = {k for k, _, _, _ in iter_entry_matches(text, es, ee)}
        missing = {k: v for k, v in overrides.items() if k not in existing}
        if missing:
            text = insert_entries(text, ee - 1, missing)
            entries.update(missing)
    return text, entries


def anxious_treat(key, val):
    v = stage2(val)
    if key == "Treat_Hurt_Before1":
        return CURED_6_10["Treat_Hurt_Before1"]
    if key == "Treat_Hurt_After1":
        return CURED_6_10["Treat_Hurt_After1"]
    return v


def main():
    text = PATH.read_text(encoding="utf-8")
    text = text.replace('"Hearts:Harvey": "3,4,5,6,7,8,9,10"', '"Hearts:Harvey": "3,4,5"')

    text, _ = patch_block(text, "0,1,2", fix_vous_key, PROX_VOUS)

    def t35(key, val):
        if key in CURED_3_5:
            return CURED_3_5[key]
        if "Вас" in val or re.search(r"\bВы\b", val):
            val = vous_to_ty(val)
        return stage1(val)

    text, entries_35 = patch_block(text, "3,4,5", t35, CURED_3_5)

    def t610(key, val):
        if key in CURED_6_10:
            return CURED_6_10[key]
        base = entries_35.get(key, val)
        if key.startswith("Treat_"):
            return anxious_treat(key, base)
        if "Phase" in key or key.startswith("Treatment_Phase") or key.startswith("Recovery_"):
            return stage2(base if key in entries_35 else val)
        return stage2(base if key in entries_35 else val)

    # Add all 3-5 keys missing from 6-10 block
    add_610 = {k: t610(k, v) for k, v in entries_35.items() if k not in CURED_6_10}
    add_610.update(CURED_6_10)
    text, _ = patch_block(text, "6,7,8,9,10", t610, add_610)

    PATH.write_text(text, encoding="utf-8")
    print(f"Done. 3-5 keys={len(entries_35)}, 6-10 overrides={len(add_610)}")


if __name__ == "__main__":
    main()
