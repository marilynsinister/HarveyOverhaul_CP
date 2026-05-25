# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets" / "Code"

EXTRA = [
    (r"(?<![а-яА-ЯёЁ])слышишь(?![а-яА-ЯёЁ])", "слышите"),
    (r"(?<![а-яА-ЯёЁ])пытайся(?![а-яА-ЯёЁ])", "пытайтесь"),
    (r"(?<![а-яА-ЯёЁ])говори(?![а-яА-ЯёЁ])", "говорите"),
    (r"(?<![а-яА-ЯёЁ])сопротивляешься(?![а-яА-ЯёЁ])", "сопротивляетесь"),
    (r"(?<![а-яА-ЯёЁ])заслуживаешь(?![а-яА-ЯёЁ])", "заслуживаете"),
    (r"(?<![а-яА-ЯёЁ])забудешь(?![а-яА-ЯёЁ])", "забудете"),
    (r"(?<![а-яА-ЯёЁ])не забывай(?![а-яА-ЯёЁ])", "не забывайте"),
    (r"(?<![а-яА-ЯёЁ])Выпей(?![а-яА-ЯёЁ])", "Выпейте"),
    (r"(?<![а-яА-ЯёЁ])остаёшься(?![а-яА-ЯёЁ])", "остаётесь"),
    (r"(?<![а-яА-ЯёЁ])переутомишься(?![а-яА-ЯёЁ])", "переутомитесь"),
    (r"(?<![а-яА-ЯёЁ])переутомилась(?![а-яА-ЯёЁ])", "переутомились"),
    (r"(?<![а-яА-ЯёЁ])привыкла(?![а-яА-ЯёЁ])", "привыкли"),
    (r"(?<![а-яА-ЯёЁ])съела(?![а-яА-ЯёЁ])", "съели"),
    (r"(?<![а-яА-ЯёЁ])навредила(?![а-яА-ЯёЁ])", "навредили"),
]


def to_vy_extra(s: str) -> str:
    for pat, repl in EXTRA:
        s = re.sub(pat, repl, s)
    return s


def block_is_vy(block: str) -> bool:
    if '"Relationship:Harvey": "Married"' in block or '"Relationship:Harvey": "Dating"' in block:
        return False
    if "MarriageDialogue" in block:
        return False
    m = re.search(r'"Hearts:Harvey": "([^"]+)"', block)
    if m:
        nums = [int(x) for x in m.group(1).split(",") if x.strip().isdigit()]
        if nums and min(nums) >= 3:
            return False
        if nums and max(nums) <= 2:
            return True
    return True


def patch_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    if '"Changes"' not in text:
        return 0
    parts = re.split(r"(\n\s*\{\s*\n\s*\"Action\")", text)
    out = [parts[0]]
    count = 0
    for i in range(1, len(parts), 2):
        block = parts[i] + (parts[i + 1] if i + 1 < len(parts) else "")
        if block_is_vy(block) and '"Entries"' in block:
            m = re.search(r'"Entries"\s*:\s*\{', block)
            if m:
                start = m.end() - 1
                depth = 0
                for j in range(start, len(block)):
                    if block[j] == "{":
                        depth += 1
                    elif block[j] == "}":
                        depth -= 1
                        if depth == 0:
                            raw = re.sub(r"^\s*//.*$", "", block[start : j + 1], flags=re.MULTILINE)
                            try:
                                entries = json.loads(raw)
                            except json.JSONDecodeError:
                                break
                            new_entries = {}
                            changed = False
                            for k, v in entries.items():
                                if isinstance(v, str):
                                    nv = to_vy_extra(v)
                                    if nv != v:
                                        changed = True
                                        count += 1
                                    new_entries[k] = nv
                                else:
                                    new_entries[k] = v
                            if changed:
                                lines = [
                                    f'        "{k}": {json.dumps(v, ensure_ascii=False)},'
                                    for k, v in new_entries.items()
                                ]
                                lines[-1] = lines[-1][:-1]
                                block = block[:start] + "{\n" + "\n".join(lines) + "\n      }" + block[j + 1 :]
                            break
        out.append(block)
    new_text = "".join(out)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
    return count


if __name__ == "__main__":
    total = 0
    for path in sorted(list(ROOT.glob("dialoguesHarvey*.json")) + list(ROOT.glob("quest_dialogues.json"))):
        n = patch_file(path)
        if n:
            print(path.name, n)
            total += n
    print("total", total)
