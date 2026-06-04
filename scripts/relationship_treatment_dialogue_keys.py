"""Add Treat_* relationship-stage keys and rename formal 0-2 keys to _Stranger_."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURE = ROOT / "assets/Code/dialoguesHarveyCure.json"
INJURY = ROOT / "assets/Code/dialoguesHarveyInjury.json"

FORMAL_MARKERS = (
    "Вы",
    "Вам",
    "Вас",
    "Ваш",
    "держите",
    "садитесь",
    "приходите",
    "не забывайте",
    "избегайте",
    "Покажите",
    "Посмотрите",
    "коснитесь",
    "встаньте",
    "расчёсывайте",
    "Можете",
    "перенапрягайтесь",
    "сообщите",
    "отпустить Вас",
)

INJURIES = [
    "Hurt",
    "BadlyHurt",
    "BruisedRibs",
    "SprainedAnkle",
    "BackStrain",
    "DeepCuts",
    "BurnWounds",
    "TornMuscles",
    "Concussion",
    "FracturedBone",
    "InfectedWound",
    "ShrapnelWounds",
    "Cold",
    "SurgicalWound",
]

TREAT_AFTER_TY = (
    "После перевязки — без нагрузки.$0#$b#Если боль усилится — сразу ко мне, не тяни.$a"
)
TREAT_BEFORE_TY = (
    "Сейчас осмотрю и обработаю.$0#$b#Покажи, где болит — начну по протоколу.$0"
)

TREAT_KEY_RE = re.compile(r'^(\s*)"(Treat_(\w+)_(Before|After))(\d+)":\s*"(.*)"\s*,?\s*$')
STAGED_KEY_RE = re.compile(
    r'^(\s*)"(Treat_(\w+)_(Before|After))_(Stranger|Acquaintance|Friend|Close|Dating|Married)_(\d+)":'
)
PREFIX_KEY_RE = re.compile(
    r'^(\s*)"(Treat_|Support_|PhaseTransition_|Recovery_Complete_)([^"]+)":\s*"(.*)"\s*,?\s*$'
)


def is_formal(text: str) -> bool:
    return any(m in text for m in FORMAL_MARKERS)


def convert_formal_to_ty(text: str) -> str:
    replacements = [
        ("Покажите", "Покажи"),
        ("покажите", "покажи"),
        ("Посмотрите", "Посмотри"),
        ("посмотрите", "посмотри"),
        ("коснитесь", "коснись"),
        ("встаньте", "встань"),
        ("Встаньте", "Встань"),
        ("избегайте", "избегай"),
        ("Избегайте", "Избегай"),
        ("приходите", "приходи"),
        ("Приходите", "Приходи"),
        ("держите", "держи"),
        ("Держите", "Держи"),
        ("расчёсывайте", "расчёсывай"),
        ("не забывайте", "не забывай"),
        ("Можете", "Можешь"),
        ("перенапрягайтесь", "перенапрягайся"),
        ("сообщите", "сообщи"),
        ("отпустить Вас", "отпустить тебя"),
        (" Вы ", " ты "),
        ("Вы ", "Ты "),
        (" Вас", " тебя"),
        ("Вас ", "Тебя "),
        (" Вам", " тебе"),
        ("Вам ", "Тебе "),
        (" Ваш", " твой"),
        ("Ваше ", "Твоё "),
        ("Ваши ", "Твои "),
        ("Вашу ", "Твою "),
        ("ваш", "твой"),
    ]
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def patch_cure_hearts_0_2(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_hearts_02 = False

    for line in lines:
        if '"Hearts:Harvey": "0,1,2"' in line:
            in_hearts_02 = True
        elif in_hearts_02 and '"Hearts:Harvey":' in line:
            in_hearts_02 = False

        normalized = line.replace("\r", "").rstrip("\n")
        m = TREAT_KEY_RE.match(normalized)
        if not (in_hearts_02 and m):
            out.append(line)
            continue
        if STAGED_KEY_RE.match(normalized):
            out.append(line)
            continue

        indent, base, injury, phase, num, body = m.groups()
        if not is_formal(body):
            out.append(line)
            continue

        new_key = f'{base}_Stranger_{num}'
        comma = "," if line.rstrip().endswith(",") else ""
        out.append(f'{indent}"{new_key}": "{body}"{comma}\n')
        changes.append(f"Treat_{injury}_{phase} → Stranger ({num})")
        continue

    return "".join(out), changes


def build_treat_stage_entries(stage: str, use_married_tone: bool) -> list[str]:
    entries: list[str] = []
    for injury in INJURIES:
        for phase in ("Before", "After"):
            if injury == "Cold" and phase == "Before":
                continue
            text = TREAT_BEFORE_TY if phase == "Before" else TREAT_AFTER_TY
            if use_married_tone and injury == "Cold":
                continue
            key = f"Treat_{injury}_{phase}_{stage}_1"
            entries.append(f'                "{key}": "{text}",')
    return entries


def inject_into_relationship_block(text: str, relationship: str, entries: list[str]) -> str:
    marker = f'"Relationship:Harvey": "{relationship}"'
    idx = text.find(marker)
    if idx < 0:
        raise RuntimeError(f"Block {relationship} not found in cure json")

    if "TREAT_* (relationship stage keys for C#)" in text[idx : idx + 4000]:
        return text

    entries_start = text.find('"Entries": {', idx)
    if entries_start < 0:
        raise RuntimeError(f"Entries for {relationship} not found")

    insert_at = entries_start + len('"Entries": {')
    block = "\n                // ================== TREAT_* (relationship stage keys for C#) ==================\n"
    block += "\n".join(entries) + "\n"
    return text[:insert_at] + block + text[insert_at:]


def patch_cure_formal_recovery_support(text: str, relationship: str | None) -> tuple[str, list[str]]:
    """In 0-2 block: Stranger keys; optional Dating/Married ty duplicates for formal Recovery/Support."""
    changes: list[str] = []
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    in_hearts_02 = False

    for line in lines:
        if '"Hearts:Harvey": "0,1,2"' in line:
            in_hearts_02 = True
        elif in_hearts_02 and '"Hearts:Harvey":' in line:
            in_hearts_02 = False

        stripped = line.rstrip("\n")
        m = PREFIX_KEY_RE.match(stripped)
        if not (in_hearts_02 and m):
            out.append(line)
            continue

        indent, prefix, rest, body = m.groups()
        full_prefix = prefix + rest
        if "_Stranger" in full_prefix or "_Dating" in full_prefix or "_Married" in full_prefix:
            out.append(line)
            continue
        if not is_formal(body):
            out.append(line)
            continue
        if not (
            full_prefix.startswith("Recovery_Complete_")
            or full_prefix == "Support_Cold"
        ):
            out.append(line)
            continue

        ty_body = convert_formal_to_ty(body)
        comma = "," if stripped.endswith(",") else ""
        out.append(f'{indent}"{full_prefix}_Stranger": "{body}"{comma}\n')
        changes.append(f"{full_prefix} → Stranger")
        if relationship:
            stage = relationship
            out.append(f'{indent}"{full_prefix}_{stage}": "{ty_body}"{comma}\n')
        continue

    return "".join(out), changes


def patch_injury_formal_phase(text: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    lines = text.splitlines(keepends=True)
    out: list[str] = []

    for line in lines:
        stripped = line.rstrip("\n")
        m = PREFIX_KEY_RE.match(stripped)
        if not m:
            out.append(line)
            continue

        indent, prefix, rest, body = m.groups()
        full_prefix = prefix + rest
        if "_Stranger_" in full_prefix or "_Dating_" in full_prefix or "_Married_" in full_prefix:
            out.append(line)
            continue
        if not is_formal(body):
            out.append(line)
            continue
        if not (
            full_prefix.startswith("PhaseTransition_")
            or full_prefix.startswith("Recovery_Complete_")
        ):
            out.append(line)
            continue

        new_key = f"{full_prefix}_Stranger"
        ty_body = convert_formal_to_ty(body)
        comma = "," if stripped.endswith(",") else ""
        out.append(f'{indent}"{new_key}": "{ty_body}"{comma}\n')
        out.append(f'{indent}"{full_prefix}_Dating": "{ty_body}"{comma}\n')
        out.append(f'{indent}"{full_prefix}_Married": "{ty_body}"{comma}\n')
        changes.append(full_prefix)
        continue

    return "".join(out), changes


def main() -> None:
    cure = CURE.read_text(encoding="utf-8")
    cure, stranger_changes = patch_cure_hearts_0_2(cure)
    cure, recovery_stranger = patch_cure_formal_recovery_support(cure, relationship=None)

    dating_entries = build_treat_stage_entries("Dating", use_married_tone=False)
    married_entries = build_treat_stage_entries("Married", use_married_tone=True)
    cure = inject_into_relationship_block(cure, "Dating", dating_entries)
    cure = inject_into_relationship_block(cure, "Married", married_entries)
    cure, recovery_dating = patch_cure_formal_recovery_support(cure, "Dating")
    cure, recovery_married = patch_cure_formal_recovery_support(cure, "Married")
    CURE.write_text(cure, encoding="utf-8")

    injury = INJURY.read_text(encoding="utf-8")
    injury, phase_changes = patch_injury_formal_phase(injury)
    INJURY.write_text(injury, encoding="utf-8")

    print(f"cure: Stranger Treat keys: {len(stranger_changes)}")
    print(f"cure: Stranger Recovery/Support: {len(recovery_stranger)}")
    print(f"cure: Dating Recovery/Support duplicates: {len(recovery_dating)}")
    print(f"cure: Married Recovery/Support duplicates: {len(recovery_married)}")
    print(f"cure: Dating Treat keys: {len(dating_entries)}")
    print(f"cure: Married Treat keys: {len(married_entries)}")
    print(f"injury: Phase/Recovery staged: {len(phase_changes)}")
    for key in phase_changes[:15]:
        print(f"  - {key}")


if __name__ == "__main__":
    main()
