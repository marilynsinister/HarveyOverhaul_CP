# -*- coding: utf-8 -*-
"""Gate dialoguesHarveyCure.json: regex patch without full JSON parse."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "assets/Code/dialoguesHarveyCure.json"
raw = path.read_text(encoding="utf-8")

FORBIDDEN = (
    "солнышко", "малышка", "котёнок", "девочка моя",
    "люблю", "не отпущу", "не позволю", "под моей защитой",
)

def to_vous(text):
    if any(w in text.lower() for w in FORBIDDEN):
        text = re.sub(r"(?i)не позволю", "недопустимо", text)
        text = re.sub(r"(?i)не отпущу", "не оставлю без наблюдения", text)
        text = re.sub(r"(?i)под моей защитой", "под медицинским наблюдением", text)
    pairs = [
        (r"\bслушалась\b", "слушались"),
        (r"\bсправилась\b", "справились"),
        (r"\bвыдержала\b", "выдержали"),
        (r"\bвыздоровела\b", "выздоровели"),
        (r"\bзажила\b", "зажило"),
        (r"\bзажил\b", "зажило"),
        (r"\bснимала\b", "снимали"),
        (r"\bбросила\b", "бросили"),
        (r"\bигнорировала\b", "игнорировали"),
        (r"\bмокнешь\b", "мокнете"),
        (r"\bне бегай\b", "не бегайте"),
        (r"\bне рискуй\b", "не рискуйте"),
        (r"\bотдыхай\b", "отдыхайте"),
        (r"\bсообщи\b", "сообщите"),
        (r"\bскажи\b", "скажите"),
        (r"\bприходи\b", "приходите"),
        (r"\bдержи\b", "держите"),
        (r"\bне расчёсывай\b", "не расчёсывайте"),
        (r"\bне жди\b", "не ждите"),
        (r"\bзови\b", "зовите"),
        (r"\bне геройствуй\b", "не геройствуйте"),
        (r"\bне стесняйся\b", "не стесняйтесь"),
        (r"\bне обижайся\b", "не обижайтесь"),
        (r"\bне игнорируй\b", "не игнорируйте"),
        (r"\bне спорь\b", "не спорьте"),
        (r"\bне вставай\b", "не вставайте"),
        (r"\bне двигайся\b", "не двигайтесь"),
        (r"\bне пытайся\b", "не пытайтесь"),
        (r"\bне снимай\b", "не снимайте"),
        (r"\bне забывай\b", "не забывайте"),
        (r"\bодна\b", "в одиночку"),
        (r"\bодной\b", "в одиночку"),
        (r"на тебя", "на Вас"),
        (r"с тобой", "с Вами"),
        (r"за тобой", "за Вами"),
        (r"к тебе", "к Вам"),
        (r"тебя", "Вас"),
        (r"тебе", "Вам"),
        (r"тобой", "Вами"),
        (r"твоими", "Вашими"),
        (r"твоих", "Ваших"),
        (r"твоему", "Вашему"),
        (r"твоей", "Вашей"),
        (r"твоё", "Ваше"),
        (r"твою", "Вашу"),
        (r"твои", "Ваши"),
        (r"твой", "Ваш"),
        (r"твоя", "Ваша"),
        (r"\bты\b", "Вы"),
    ]
    for pat, repl in pairs:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text

# Extract first block entries only (before first When Hearts 6)
first_block_match = re.search(
    r'\{\s*"Action": "EditData",\s*"Target": "Characters/Dialogue/Harvey",\s*"Entries": \{(.*?)\n            \}\n        \},\n        \{\s*"Action": "EditData",\s*"Target": "Characters/Dialogue/Harvey",\s*"When": \{\s*"Hearts:Harvey": "6',
    raw,
    re.DOTALL,
)
if not first_block_match:
    raise SystemExit("first block not found")

block_body = first_block_match.group(1)
entry_re = re.compile(r'^\s*"([^"]+)": "((?:[^"\\]|\\.)*)",?\s*$', re.MULTILINE)
entries = entry_re.findall(block_body)
print(f"parsed {len(entries)} keys from first block")

fixes = {
    "topicHealthCheckup": "%Харви после осмотра кивает с одобрением.#$b#Показатели в норме, но рекомендую не пропускать профилактику.#$b#При изменениях самочувствия — сразу в клинику.$0#%Он назначает дату следующего осмотра.",
    "buffAntibioticsTreatment": "Антибиотики действуют.$0#$b#Курс нельзя прерывать.$a#$b#Даже если стало лучше — до конца по схеме.$0#$b#Иначе риск осложнений.$a",
    "topicFracturedBoneCured": "%Харви изучает рентген.#$b#Срастание на снимке в норме — гипс снимаем. Нагрузки возвращайте постепенно: сначала лёгкие дела, без шахты и тяжёлых мешков.$0#%Он назначает короткую программу реабилитации.",
}

vous_lines = []
for key, val in entries:
    if key in fixes:
        vous_lines.append((key, fixes[key]))
    elif re.search(r"\b(ты|тебя|тебе|тво[ейюяёи])\b", val, re.I):
        vous_lines.append((key, to_vous(val)))
    else:
        vous_lines.append((key, val))

lines = [
    "        {",
    '            "Action": "EditData",',
    '            "Target": "Characters/Dialogue/Harvey",',
    '            "Priority": "Late",',
    '            "When": {',
    '                "Hearts:Harvey": "0,1,2"',
    "            },",
    '            "Entries": {',
]
for key, val in vous_lines:
    esc = val.replace("\\", "\\\\").replace('"', '\\"')
    lines.append(f'                "{key}": "{esc}",')
lines.append("            }")
lines.append("        },")
block_text = "\n".join(lines)

marker = '"Target": "Characters/Dialogue/Harvey",\n            "Entries": {'
when_3 = '"Target": "Characters/Dialogue/Harvey",\n            "When": {\n                "Hearts:Harvey": "3,4,5,6,7,8,9,10"\n            },\n            "Entries": {'
if marker not in raw:
    raise SystemExit("marker missing")
raw = raw.replace(marker, when_3, 1)
raw = raw.replace('    "Changes": [\n        {', '    "Changes": [\n' + block_text + "\n        {", 1)

# Fix merged health/buff line in 3+ block
raw = raw.replace(
    '"topicHealthCheckup": "%Харви после осмотра смотрит на тебя с одобрением.#$b#Ты здорова, но не забывай, что твой организм требует особого внимания. Я буду следить за твоим состоянием, и если что-то почувствуешь — сразу приходи ко мне.$0#%Он назначает дату следующего осмотра и напоминает о важности профилактики.","buffAntibioticsTreatment":',
    '"topicHealthCheckup": "%Харви после осмотра смотрит на тебя с одобрением.#$b#Ты здорова, но не забывай, что твой организм требует особого внимания. Я буду следить за твоим состоянием, и если что-то почувствуешь — сразу приходи ко мне.$0#%Он назначает дату следующего осмотра и напоминает о важности профилактики.",\n                "buffAntibioticsTreatment":',
)

path.write_text(raw, encoding="utf-8")
print("cure gate OK")
