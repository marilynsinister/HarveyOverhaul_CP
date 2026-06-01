#!/usr/bin/env python3
"""Adjust Speed/MovementSpeed in CP buff JSON without reformatting files."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODE = ROOT / "assets" / "Code"

# Leg / mobility injuries: may keep Speed or MovementSpeed at -1
LEG_INJURY_IDS = {
    "buffSprainedAnkle",
    "HarveyMod_SprainedAnkle_Acute",
    "HarveyMod_SprainedAnkle_Recovery",
    "buffFracturedBone",
    "HarveyMod_FracturedBone_Acute",
    "HarveyMod_FracturedBone_Cast",
    "HarveyMod_FracturedBone_Recovery",
    "HarveyMod_ImpairedMobility",
}

# Stress buffs: negative speed -> remove (0)
STRESS_FILE = CODE / "buffsStress.json"

# Heavy / critical injury & care debuffs: cap at -1
HEAVY_CAP_IDS = {
    "buffPainFlare",
    "buffTornMuscles",
    "buffConcussion",
    "buffFracturedBone",
    "buffShrapnelWounds",
    "buffAlcoholPoisoning",
    "HarveyMod_Sepsis",
    "HarveyMod_ImpairedMobility",
    "buffEmergencySupervision",
    "buffConstantSupervision",
    "buffForcedSedation",
    "buffPostSurgicalCare",
    "HarveyMod_FracturedBone_Acute",
    "HarveyMod_Concussion_Acute",
    "HarveyMod_TornMuscles_Acute",
    "HarveyMod_BadlyHurt_OutpatientCare",
    "buffHarveyRehab",
}

LIGHT_INJURY_ZERO_MS = {
    "buffBruisedRibs",
    "buffBackStrain",
    "buffCold",
    "HarveyMod_Cold_Acute",
    "HarveyMod_Cold_Recovery",
}

MEDIUM_MS_CAP = {
    "buffDeepCuts",
    "buffBurnWounds",
    "buffTornMuscles",
    "buffConcussion",
    "buffFracturedBone",
    "buffShrapnelWounds",
}


def parse_speed(line: str) -> tuple[str, float] | None:
    m = re.search(r'"(Speed|MovementSpeed)":\s*(-?\d+(?:\.\d+)?)', line)
    if not m:
        return None
    return m.group(1), float(m.group(2))


def remove_line(lines: list[str], idx: int) -> None:
    line = lines[idx]
    if line.rstrip().endswith(','):
        del lines[idx]
        return
    # last effect field: drop comma from previous line
    if idx > 0 and lines[idx - 1].rstrip().endswith(','):
        lines[idx - 1] = lines[idx - 1].rstrip().rstrip(',') + '\n'
    del lines[idx]


def set_speed_line(line: str, key: str, value: int | float) -> str:
    if isinstance(value, float) and value == int(value):
        value = int(value)
    return re.sub(
        rf'"{key}":\s*-?\d+(?:\.\d+)?',
        f'"{key}": {value}',
        line,
        count=1,
    )


def process_file(path: Path, changes: list[tuple]) -> int:
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    current_id: str | None = None
    in_effects = False
    n = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        m_id = re.match(r'\s*"([^"]+)":\s*\{', line)
        if m_id and '"Effects"' not in line:
            current_id = m_id.group(1)
            in_effects = False
        if '"Effects":' in line and '{' in line:
            in_effects = True
        if in_effects and line.strip() == '},' or (line.strip() == '}' and i + 1 < len(lines)):
            in_effects = False

        if in_effects and current_id:
            parsed = parse_speed(line)
            if parsed:
                key, old = parsed
                new_val, reason = decide(path.name, current_id, key, old)
                if new_val is None:
                    remove_line(lines, i)
                    changes.append((current_id, key, old, 0, reason))
                    n += 1
                    continue
                if new_val != old:
                    lines[i] = set_speed_line(line, key, new_val)
                    changes.append((current_id, key, old, new_val, reason))
                    n += 1
                    i += 1
                    continue
        i += 1

    if n:
        path.write_text(''.join(lines), encoding='utf-8', newline='')
    return n


def decide(filename: str, buff_id: str, key: str, old: float) -> tuple[float | None, str]:
    if old >= 0:
        return old, 'positive unchanged'

    if filename == 'buffsStress.json':
        return None, 'stress: no speed penalty'

    if filename == 'buffsMedicalCare.json':
        if buff_id == 'HarveyMod_Prescription_Rest':
            return None, 'prescription rest: no fractional speed'
        if buff_id == 'buffHarveyRehab' and old == -1:
            return None, 'rehab: stamina-only reminder'

    if filename == 'buffsCure.json':
        if buff_id == 'buffStrictSupervision' and key == 'MovementSpeed':
            return None, 'supervision: mobility via stamina/health buff'
        if buff_id in HEAVY_CAP_IDS or 'Acute' in buff_id or 'Sedation' in buff_id or 'Supervision' in buff_id:
            return -1, 'critical care cap -1'
        if old < -1:
            return -1, 'capped to -1'

    if filename == 'buffsInjury.json':
        if buff_id in LEG_INJURY_IDS and key in ('Speed', 'MovementSpeed'):
            return -1, 'leg/mobility injury max -1'
        if buff_id in LIGHT_INJURY_ZERO_MS and key == 'MovementSpeed':
            return None, 'light injury: no movement speed penalty'
        if buff_id in MEDIUM_MS_CAP and key == 'MovementSpeed':
            return -1, 'medium injury cap -1'
        if key == 'MovementSpeed' and old < -1:
            return -1, 'movement capped -1'
        if key == 'Speed' and buff_id in HEAVY_CAP_IDS:
            return -1, 'heavy injury cap -1'
        if key == 'Speed' and buff_id in ('buffCold', 'HarveyMod_Cold_Acute', 'HarveyMod_Cold_Recovery'):
            return None, 'cold: no speed penalty'
        if key == 'Speed' and old < -1:
            return -1, 'speed capped -1'

    if old < -1:
        return -1, 'global cap -1'
    return old, 'already within cap'


def main():
    files = [
        CODE / 'buffsStress.json',
        CODE / 'buffsInjury.json',
        CODE / 'buffsCure.json',
        CODE / 'buffsMedicalCare.json',
    ]
    all_changes: list[tuple] = []
    for f in files:
        if f.exists():
            process_file(f, all_changes)

    out = ROOT / 'docs' / 'balance-speed-penalties.md'
    lines = [
        '# Balance: speed penalties (buffs)\n',
        '\nСмягчены штрафы к скорости в Content Patcher (`HarveyOverhaul [CP]`). '
        'Проекты `HarveyOverhaulInjury` и `HarveyStressMeter` (C#) в рабочей копии не найдены — '
        'если там есть динамические модификаторы скорости, их нужно проверить отдельно в исходниках.\n',
        '\n| Бафф | Было Speed | Стало Speed | Причина |\n',
        '|---|---:|---:|---|\n',
    ]
    for buff_id, key, old, new, reason in sorted(all_changes, key=lambda x: (x[0], x[1])):
        old_s = f'{key} {old:g}' if old != 0 else f'{key} {old:g}'
        new_s = '—' if new == 0 else f'{key} {new:g}'
        lines.append(f'| `{buff_id}` | {old:g} | {new_s} | {reason} |\n')
    out.parent.mkdir(parents=True, exist_ok=True)
    if all_changes:
        out.write_text(''.join(lines), encoding='utf-8')
        print(f'Updated {len(all_changes)} effect lines; wrote {out}')
    else:
        print(f'No JSON changes; left existing doc at {out}')


if __name__ == '__main__':
    main()
