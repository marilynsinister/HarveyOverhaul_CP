"""Переводит невалидные ключи Effects в Data/Buffs на поля BuffAttributesData (SDV 1.6).

Игра молча игнорирует неизвестные поля (Stamina, Health, MovementSpeed, Luck, StaminaRegen,
DefenseMultiplier), поэтому такие эффекты не работали.

    python scripts/fix_buff_effect_keys.py          # dry-run
    python scripts/fix_buff_effect_keys.py --write
"""
import glob
import re
import sys

LUCK_CAP = 3
DEFENSE_MIN = -10


def fmt(v):
    v = round(v, 3)
    return str(int(v)) if float(v).is_integer() else str(v)


def convert(pairs):
    out = {}
    order = []

    def add(key, value):
        if key not in out:
            out[key] = 0.0
            order.append(key)
        out[key] += value

    for key, value in pairs:
        if key == "MovementSpeed":
            add("Speed", value)
        elif key == "Luck":
            add("LuckLevel", max(-LUCK_CAP, min(LUCK_CAP, value)))
        elif key == "Stamina":
            add("MaxStamina", value)
        elif key == "Health":
            step = round(value / 10) or (1 if value > 0 else -1)
            add("Defense", step)
        elif key == "StaminaRegen":
            add("MaxStamina", 15 * value if value < 0 else 10 * value)
        elif key == "DefenseMultiplier":
            add("Defense", round(value * 10) or (1 if value > 0 else -1))
        else:
            add(key, value)
    if "Defense" in out:
        out["Defense"] = max(DEFENSE_MIN, out["Defense"])
    return [(k, out[k]) for k in order]


BAD = {"MovementSpeed", "Luck", "Stamina", "Health", "StaminaRegen", "DefenseMultiplier"}
BLOCK = re.compile(r'("Effects"\s*:\s*\{)([^{}]*)(\})')
PAIR = re.compile(r'"(\w+)"\s*:\s*(-?[\d.]+)')


def main(write):
    changed = 0
    for path in glob.glob("assets/**/*.json", recursive=True):
        text = open(path, encoding="utf-8-sig").read()

        def repl(m):
            nonlocal changed
            body = m.group(2)
            pairs = [(k, float(v)) for k, v in PAIR.findall(body)]
            if not any(k in BAD for k, _ in pairs):
                return m.group(0)
            new = convert(pairs)
            changed += 1
            print(f"{path}: {dict(pairs)} -> {dict(new)}")
            if "\n" in body:
                indent = re.search(r"\n([ \t]*)\"", body).group(1)
                close_indent = re.search(r"\n([ \t]*)$", body)
                close_indent = close_indent.group(1) if close_indent else ""
                inner = ",\n".join(f'{indent}"{k}": {fmt(v)}' for k, v in new)
                return f"{m.group(1)}\n{inner}\n{close_indent}{m.group(3)}"
            inner = ", ".join(f'"{k}": {fmt(v)}' for k, v in new)
            return f"{m.group(1)} {inner} {m.group(3)}"

        new_text = BLOCK.sub(repl, text)
        if write and new_text != text:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new_text)
    print(f"blocks changed: {changed}{'' if write else ' (dry-run)'}")


if __name__ == "__main__":
    main("--write" in sys.argv)
