import re
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "assets/Code/dialoguesHarveyCure.json"
raw = p.read_text(encoding="utf-8")
start = raw.index('"Hearts:Harvey": "0,1,2"')
end = raw.index('"Hearts:Harvey": "3,4,5,6,7,8,9,10"')
block = raw[start:end]
pairs = [
    ("почувствуешь", "почувствуете"),
    ("остановись", "остановитесь"),
    ("дай знать", "дайте знать"),
    ("будь ", "будьте "),
    ("работаешь", "работаете"),
    ("избегай ", "избегайте "),
    ("не работай", "не работайте"),
    ("слушалась", "следовали"),
    ("отдыхала", "отдыхали"),
    ("следовала", "следовали"),
    ("твоего", "Вашего"),
    ("перенапрягайся", "перенапрягайтесь"),
]
for a, b in pairs:
    block = re.sub(a, b, block, flags=re.IGNORECASE)
block = re.sub(r"\. не ", ". Не ", block)
block = re.sub(r"\. если ", ". Если ", block, flags=re.IGNORECASE)
p.write_text(raw[:start] + block + raw[end:], encoding="utf-8")
print("OK")
