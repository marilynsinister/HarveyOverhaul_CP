"""Чинит setSkipActions в событиях, написанных вручную (не генераторами).

Для каждой пропускаемой сцены список заменяется на complete_skip(): только trigger actions и все эффекты
тела сцены вне веток выбора (темы, письма, дружба, предметы, action …). Если setSkipActions нет — добавляется
после `skippable`. Правка идёт по исходному тексту, так что комментарии и переносы строк сохраняются.

Запуск:  python -I scripts/fix_skip_actions.py [--dry]
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from skip_actions import complete_skip  # noqa: E402
from validate_event_coords import CP_ROOT, included_files, read_jsonc, split_commands  # noqa: E402

# Эти файлы пишут генераторы scripts/build_*.py — их чинит event_builder / complete_skip при сборке.
GENERATED = {
    "eventsAdult.json", "eventsArc3.json", "clinicSeasonal.json", "festivalsHarvey.json", "eventsHarveyLife.json",
    "eventsMarriage.json", "eventsMarriageRotation.json", "eventsScars.json", "eventsExamConsent.json",
}


def value_span(raw, key_pos):
    """Начало и конец строки-значения JSON для ключа, начинающегося в key_pos (на открывающей кавычке)."""
    i = key_pos + 1
    while raw[i] != '"':
        i += 2 if raw[i] == "\\" else 1
    i = raw.index('"', i + 1)  # открывающая кавычка значения
    start = i + 1
    j = start
    while raw[j] != '"':
        j += 2 if raw[j] == "\\" else 1
    return start, j


def raw_key_pos(raw, key):
    escaped = key.replace("\\", "\\\\").replace('"', '\\"')
    pos = raw.find('"' + escaped + '"')
    if pos < 0:
        raise KeyError(key)
    return pos


def fix_file(rel, dry):
    path = os.path.join(CP_ROOT, rel)
    raw = open(path, encoding="utf-8-sig", newline="").read()
    doc = read_jsonc(path)
    changed = []
    for change in doc.get("Changes", []):
        if not str(change.get("Target", "")).startswith("Data/Events/"):
            continue
        for key, script in (change.get("Entries") or {}).items():
            if not isinstance(script, str):
                continue
            cmds = split_commands(script)
            body = cmds[3:]
            if "skippable" not in body:
                continue
            skip_cmd = next((c for c in body if c.startswith("setSkipActions")), None)
            old = [a.strip() for a in skip_cmd[len("setSkipActions"):].split("#") if a.strip()] if skip_cmd else []
            rest = [c for c in body if c != skip_cmd]
            new = complete_skip(old, rest)
            if new == old:
                continue
            start, end = value_span(raw, raw_key_pos(raw, key))
            value = raw[start:end]
            new_cmd = "setSkipActions " + "#".join(new)
            if skip_cmd and not new:
                m = re.search(r"setSkipActions[^/]*/\s*", value)
                value = value[:m.start()] + value[m.end():]
            elif skip_cmd:
                m = re.search(r"setSkipActions[^/]*", value)
                value = value[:m.start()] + new_cmd + value[m.end():]
            elif new:
                m = re.search(r"skippable\s*/(\s*)", value)
                indent = m.group(1)
                value = value[:m.end()] + new_cmd + "/" + (indent or "") + value[m.end():]
            else:
                continue
            raw = raw[:start] + value + raw[end:]
            changed.append((key.split("/")[0], old, new))
    if changed and not dry:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(raw)
    return changed


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    dry = "--dry" in sys.argv
    for rel in included_files():
        if os.path.basename(rel) in GENERATED:
            continue
        try:
            changed = fix_file(rel, dry)
        except Exception as exc:  # noqa: BLE001
            print(f"!! {rel}: {exc}")
            continue
        for eid, old, new in changed:
            print(f"{os.path.basename(rel)} {eid}\n   было:  {'#'.join(old) or '—'}\n   стало: {'#'.join(new)}")


if __name__ == "__main__":
    main()
