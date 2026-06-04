#!/usr/bin/env python3
"""Generate docs/event-exit-audit.md from CP event files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "assets" / "Code"
OUT = ROOT / "docs" / "event-exit-audit.md"
ACTIVE = {"events.json", "eventsCare.json", "eventsMineRescue.json", "eventsGotoroForestRescue.json"}
FILES = sorted(ACTIVE | {"events_for_mode_new_formatted.json"})


def read_string_value(text: str, start: int) -> tuple[str, int]:
    i = start
    out = []
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            out.append(text[i : i + 2])
            i += 2
            continue
        if c == '"':
            return "".join(out), i + 1
        out.append(c)
        i += 1
    return "".join(out), i


def read_json_key(text: str, start: int) -> tuple[str | None, int]:
    """Read JSON key at opening double-quote."""
    if start >= len(text) or text[start] != '"':
        return None, start
    i = start + 1
    chars = []
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            chars.append(text[i : i + 2])
            i += 2
            continue
        if c == '"':
            key = "".join(chars)
            m = re.match(r'\s*:\s*"', text[i + 1 :])
            if m:
                return key, i + 1 + m.end()
            return None, start + 1
        chars.append(c)
        i += 1
    return None, start


def find_entries_blocks(text: str):
    for tm in re.finditer(r'"Target"\s*:\s*"([^"]*Data/Events[^"]*)"', text):
        target = tm.group(1)
        em = re.search(r'"Entries"\s*:\s*\{', text[tm.start() :])
        if not em:
            continue
        start = tm.start() + em.end()  # after opening {
        depth = 1
        i = start
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        block = text[start : i - 1]
        p = 0
        while p < len(block):
            while p < len(block) and block[p] in " \t\r\n,":
                p += 1
            if p >= len(block):
                break
            if p + 1 < len(block) and block[p : p + 2] == "//":
                nl = block.find("\n", p)
                p = len(block) if nl == -1 else nl + 1
                continue
            if block[p] != '"':
                break
            key, val_start = read_json_key(block, p)
            if not key:
                break
            script, end_pos = read_string_value(block, val_start)
            p = end_pos
            yield target, key, script


def parse_event(target, eid, script, filename):
    lines = [ln.strip() for ln in script.split("/") if ln.strip()]
    header = lines[0] if lines else ""
    skippable = any("skippable" in ln for ln in lines[:12])
    skip_actions = next((ln for ln in lines if ln.startswith("setSkipActions")), "")
    change_locs = [ln.replace("changeLocation ", "").strip("/") for ln in lines if ln.startswith("changeLocation")]
    warps = [ln for ln in lines if re.match(r"^warp farmer", ln)]
    ends = [ln for ln in lines if re.match(r"^end(\s|$|dialogue|position|warpOut|invisible|newDay)", ln)]
    short = eid.split("/")[0]
    locs = [x.strip().replace("Data/Events/", "") for x in target.split(",")]
    return {
        "id": short,
        "file": filename,
        "active": filename in ACTIVE,
        "locs": locs,
        "header": header,
        "skippable": skippable,
        "skip_actions": skip_actions,
        "change_locs": change_locs,
        "last_change": change_locs[-1] if change_locs else "",
        "last_warp": warps[-1] if warps else "",
        "last_end": ends[-1] if ends else "(нет end)",
        "lines": lines,
    }


def story_summary(eid, script, header):
    s = script.lower()
    idl = eid.lower()
    tags = []
    if "minerescue" in idl or "topicminerescue" in s:
        tags.append("спасение в шахте")
    if "mineinterception" in idl:
        tags.append("перехват в шахте (раны)")
    if "emergencycare" in idl or "exhaustion" in idl or "treatmentcollapse" in idl:
        tags.append("принудительная госпитализация")
    if "rescueroperation" in idl or "topicrescueoperation" in s:
        tags.append("спасение после ДТП/лес")
    if "nightcrisis" in idl:
        tags.append("ночной кризис → клиника")
    if "latenightcollapse" in idl:
        tags.append("ночной коллапс → капельница")
    if "passedout" in idl or "passedout" in s or "потеряла сознание" in s or "обморок" in s:
        tags.append("обморок")
    if "firsttreatment" in idl or "лечен" in s:
        tags.append("лечение/осмотр")
    if "stormcomfort" in idl or "гроз" in s:
        tags.append("гроза/укрытие")
    if "gotoro" in idl:
        tags.append("Gotoro flashback в лесу")
    if "harveyoverhaulstory" in idl.lower():
        tags.append("сюжетная арка доверия")
    if "harveyoverhaulromance" in idl.lower():
        tags.append("романтическая арка")
    if "birthday" in idl:
        tags.append("ДР в клинике")
    if "checkup" in idl or "medicalcheck" in idl:
        tags.append("медосмотр")
    if "firstmeeting" in idl or "firstvisit" in idl:
        tags.append("знакомство")
    if "balloon" in idl or "harveyballoon" in s:
        tags.append("ванilla balloon override")
    if not tags:
        if header.startswith("continue"):
            tags.append("сцена дня")
        elif eid.split("/")[0] in ("acceptWalk", "irregularEating", "declineFood", "refuseCheckup", "HarveySkullPromise", "leaveHospital"):
            tags.append("ветка/fork")
        else:
            tags.append("локальная сцена")
    return "; ".join(tags[:4])


def start_pos(e, script):
    m = re.search(r"farmer\s+(-?\d+)\s+(-?\d+)", script[:500])
    if m:
        return f"{e['locs'][0]} @ {m.group(1)},{m.group(2)}"
    if e["header"].startswith("continue"):
        return f"{e['locs'][0]} (continue — текущая позиция)"
    if e["header"].startswith("none") and "-1000 -1000" in script[:120]:
        return "off-map → warp в сцене"
    hp = e["header"].split()
    if len(hp) >= 2 and hp[0] not in ("none", "continue") and re.match(r"-?\d+", hp[0]):
        return f"{e['locs'][0]} @ {hp[0]},{hp[1]}"
    return f"{e['locs'][0]} ({e['header'][:35]})"


def expected_pos(e, script):
    if e["last_change"]:
        loc = e["last_change"]
        wm = re.search(r"warp farmer\s+(\d+)\s+(\d+)", e["last_warp"] or "")
        if wm:
            return f"{loc} @ {wm.group(1)},{wm.group(2)}"
        return loc
    if "end position" in e["last_end"]:
        m = re.search(r"end position\s+(\d+)\s+(\d+)", e["last_end"])
        if m:
            return f"{e['locs'][0]} @ {m.group(1)},{m.group(2)}"
    if e["last_end"].strip() == "end newDay":
        if e["last_change"] == "Hospital":
            return "Hospital (новый день, ночёвка)"
        return "новый день на месте последнего warp"
    # infer from dialogue
    sl = script.lower()
    if "выведу" in sl or "наверх" in sl and e["locs"][0] == "Mine" and not e["last_change"]:
        return "выход из шахты (Town/Mine entrance) — не реализовано"
    if "просыпаешься" in sl and "FarmHouse" in e["locs"]:
        return "FarmHouse (кровать)"
    return e["locs"][0] + " (без смены локации)"


def classify(e, script):
    end = e["last_end"].strip()
    trig = e["locs"][0]
    sl = script.lower()

    if e["id"] == "eventHarveyMineInterception":
        return "HIGH", "Частично", "После «выведу наверх» добавить `changeLocation Mine` warp у выхода или `end position` у лифта; setSkipActions с тем же warp"

    if e["id"] == "eventRescueOperation":
        if not e["skip_actions"]:
            return "MEDIUM", "Нет", "Длинная цепочка локаций; `setSkipActions changeLocation Hospital#warp farmer 20 5` (или end position в Hospital)"
        return "LOW", "Да", "—"

    if e["id"] in ("eventHarveyMineRescue", "eventHarveyMineRescueDating", "eventHarveyMinorMineRescue"):
        if e["skippable"] is False and not e["skip_actions"]:
            return "MEDIUM", "N/A", "Нет skippable — OK; при желании: `end position 20 5` вместо end dialogue для фиксации койки"
        return "MEDIUM", "N/A", "changeLocation Hospital + end dialogue; рекомендуется `end position 20 5` или setSkipActions warp"

    if e["id"] in ("eventHarveyMineRescueMorning", "eventHarveyMineRescueMorningDating"):
        return "LOW", "N/A", "Сюжет: пробуждение дома (ветка если C# не сделал warp в шахте); согласовать текст с фактической локацией"

    if e["id"] in ("eventHarveyEmergencyCare", "eventHarveyExhaustion", "eventHarveyTreatmentCollapse"):
        if e["skippable"] and not e["skip_actions"]:
            return "MEDIUM", "Нет", f"setSkipActions changeLocation Hospital#warp farmer {'20 5' if '20 5' in script else '14 6'}"
        return "LOW", "N/A" if not e["skippable"] else "Частично", "—"

    if e["id"] == "eventHarveyCheckHealthFarmer":
        if not e["skip_actions"]:
            return "MEDIUM", "Нет", "setSkipActions changeLocation Hospital#warp farmer 20 5 перед end dialogue"
        return "LOW", "Да", "—"

    if e["id"] == "eventHarveyStormComfortFarm":
        return "MEDIUM", "Частично", "Ветка «клиника» в quickQuestion делает changeLocation; финальный end на Farm — OK для других веток; для ветки клиники end сразу после warp (без возврата fade)"

    if e["id"] in ("HarveyMod_NightCrisis_Dating", "HarveyMod_NightCrisis_PreDating"):
        return "LOW", "Частично", "end newDay после Hospital — штатно; setSkipActions: warp 10 7 + changeLocation Hospital"

    if e["id"] == "eventHarveyLateNightCollapse":
        if not e["skip_actions"]:
            return "MEDIUM", "Нет", "setSkipActions changeLocation Hospital#warp farmer 20 5"
        return "LOW", "Да", "—"

    if e["id"] == "eventHarveyStormComfortMine":
        if not e["skip_actions"]:
            return "MEDIUM", "Нет", "setSkipActions changeLocation Town#warp farmer 72 22"
        return "LOW", "Да", "—"

    if e["id"] == "acceptWalk":
        return "MEDIUM", "Частично", "После Forest-сцены: `end position 51 13` или warp обратно на Farm при отказе skip"

    if e["id"] == "eventHarveySkullCavePrevention":
        return "MEDIUM", "Частично", "Сюжет «домой», но end в SkullCave; добавить warp/warpOut или changeLocation"

    if e["last_change"] and trig not in (e["last_change"],) and end in ("end",) and not end.startswith("end position") and "newDay" not in end:
        if e["last_warp"]:
            if e["skippable"] and not e["skip_actions"]:
                return "MEDIUM", "Нет", f"setSkipActions changeLocation {e['last_change']}# + {e['last_warp']}"
            return "LOW", "Да", "—"
        if e["skippable"] and not e["skip_actions"]:
            return "HIGH", "Нет", f"setSkipActions changeLocation {e['last_change']}# + финальный warp farmer"
        return "MEDIUM", "Частично", f"Заменить `end` на `end position X Y` в {e['last_change']}"

    if e["last_change"] and "end dialogue" in end and not e["skip_actions"] and e["skippable"]:
        return "MEDIUM", "Нет", f"setSkipActions для {e['last_change']} + last warp"

    if end.startswith("end position"):
        return "LOW", "Да", "—"

    if not e["last_change"]:
        return "LOW", "Да" if e["skippable"] else "N/A", "—"

    return "LOW", "Да", "—"


def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


rows = []
for fn in FILES:
    path = BASE / fn
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    for target, eid, script in find_entries_blocks(text):
        e = parse_event(target, eid, script, fn)
        risk, skip_safe, fix = classify(e, script)
        rows.append({
            **e,
            "story": story_summary(eid, script, e["header"]),
            "start": start_pos(e, script),
            "expected": expected_pos(e, script),
            "risk": risk,
            "skip_safe": skip_safe,
            "fix": fix,
        })

rows.sort(key=lambda r: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[r["risk"]], r["file"], r["id"]))

lines = [
    "# Аудит выхода из Content Patcher-событий (HarveyOverhaul [CP])",
    "",
    "Дата: 2026-06-04. Проверены все файлы с `Target: Data/Events/*`, подключённые в `content.json`:",
    "`events.json`, `eventsCare.json`, `eventsMineRescue.json`, `eventsGotoroForestRescue.json`.",
    "",
    "Файл `events_for_mode_new_formatted.json` **не включён** в `content.json` — отмечен отдельно в конце.",
    "",
    "## Легенда",
    "",
    "| Risk | Значение |",
    "|------|----------|",
    "| **HIGH** | Сюжетно игрок должен быть в другой локации, но событие заканчивается обычным `end` без фиксации позиции |",
    "| **MEDIUM** | Есть `changeLocation`/`warp`, но финальная позиция неочевидна или skip может сломать результат |",
    "| **LOW** | Обычная сцена без переноса, либо корректный `end position` / `end newDay` / `end dialogue` после warp |",
    "",
    "## Сводная таблица",
    "",
    "| EventId | File | Start location | Story result | Current ending | Skip-safe? | Risk | Recommended fix |",
    "|---------|------|----------------|--------------|----------------|------------|------|-----------------|",
]

for r in rows:
    active_mark = "" if r["active"] else " *(не в content.json)*"
    ending = r["last_end"]
    if r["last_change"]:
        ending += f" (+ changeLocation {r['last_change']})"
    lines.append(
        f"| `{r['id']}` | `{r['file']}`{active_mark} | {md_escape(r['start'])} | {md_escape(r['story'])} → **{md_escape(r['expected'])}** | `{md_escape(ending[:80])}` | {r['skip_safe']} | **{r['risk']}** | {md_escape(r['fix'])} |"
    )

# Priority section
high = [r for r in rows if r["risk"] == "HIGH"]
med = [r for r in rows if r["risk"] == "MEDIUM"]

lines += [
    "",
    f"**Всего событий:** {len(rows)} (HIGH: {len(high)}, MEDIUM: {len(med)}, LOW: {len(rows)-len(high)-len(med)})",
    "",
    "## Приоритетные находки",
    "",
]

sections = [
    ("Спасение из шахты / госпитализация", ["eventHarveyMineRescue", "eventHarveyMineRescueDating", "eventHarveyMinorMineRescue", "eventHarveyMineRescueMorning", "eventHarveyMineInterception", "eventHarveyMineRescueMorningDating"]),
    ("Обморок / коллапс / принудительная клиника", ["eventHarveyEmergencyCare", "eventHarveyExhaustion", "eventHarveyTreatmentCollapse", "eventHarveyLateNightCollapse", "eventHarveyCheckHealthFarmer", "eventHarveyTreatmentCollapse", "eventStayInHospital"]),
    ("Спасение / перенос в клинику (сюжет)", ["eventRescueOperation", "HarveyMod_NightCrisis_Dating", "HarveyMod_NightCrisis_PreDating"]),
    ("Гроза / changeLocation", ["eventHarveyStormComfortFarm", "eventHarveyStormComfortMine", "eventHarveyStormComfortDesert"]),
]

for title, ids in sections:
    lines.append(f"### {title}")
    lines.append("")
    for i in ids:
        matches = [r for r in rows if r["id"] == i]
        for r in matches:
            lines.append(f"- **`{r['id']}`** ({r['file']}): {r['risk']} — {r['fix']}")
    lines.append("")

lines += [
    "## Примечания по механике SDV",
    "",
    "1. Обычный `end` после `changeLocation` + `warp farmer` **обычно** оставляет игрока в новой локации, если warp успел выполниться.",
    "2. При **skip** (`skippable` без `setSkipActions`) все команды после точки пропуска не выполняются → игрок остаётся в **стартовой** локации триггера.",
    "3. `end dialogue` / `end position X Y` / `end newDay` явнее фиксируют финальное состояние.",
    "4. События с ключом `continue/` используют текущую позицию игрока; риск ниже, если нет `changeLocation`.",
    "5. `eventHarveyEmergencyCare` / `eventHarveyExhaustion` вызываются из C# (Injury) — триггерная локация может не совпадать с Data/Events/Hospital.",
    "",
]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {OUT} ({len(rows)} events)")
