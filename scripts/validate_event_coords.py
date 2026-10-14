"""
Проверка координат событий по реальным картам (SVE, Alchemistry Hospital, ванильные tmx).

Прогоняет команды каждого события: стартовые позиции, warp, move (с промежуточными клетками),
changeLocation, ignoreCollisions — и сообщает, где актёр встаёт или проходит через стену/пустоту.
Farm/FarmHouse не проверяются: их карта зависит от типа фермы и улучшения дома.

Запуск:  python -I scripts/validate_event_coords.py [путь к Mods]
"""
import base64
import gzip
import json
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
CP_ROOT = os.path.dirname(HERE)
MYMODS = os.path.dirname(CP_ROOT)
MODS = sys.argv[1] if len(sys.argv) > 1 else r"D:\Games\Steam\steamapps\common\Stardew Valley\Mods"
SVE = os.path.join(MODS, "Stardew Valley Expanded", "[CP] Stardew Valley Expanded", "assets", "Maps")
VANILLA = os.path.join(MYMODS, "HarveyOverhaulInjury", "tmpMap", "vanilla", "maps")

# Что реально стоит в игре: Alchemistry заменяет Hospital, SVE — города и свои локации.
MAP_FILES = {
    "Hospital": os.path.join(MODS, "Alchemistry", "[CP] Alchemistry", "assets", "Maps", "MapPatches", "Hospital.tmx"),
    "Town": os.path.join(SVE, "Locations", "Town.tmx"),
    "Forest": os.path.join(SVE, "Locations", "Forest.tmx"),
    "Beach": os.path.join(SVE, "Locations", "Beach.tmx"),
    "BusStop": os.path.join(SVE, "Locations", "BusStop.tmx"),
    "Mountain": os.path.join(SVE, "Locations", "Mountain.tmx"),
    "Custom_AdventurerSummit": os.path.join(SVE, "NewLocations", "AdventurerSummit.tmx"),
    "Custom_BlueMoonVineyard": os.path.join(SVE, "NewLocations", "BlueMoonVineyard.tmx"),
    "Custom_SpriteSpring": os.path.join(SVE, "NewLocations", "SpriteSpring2.tmx"),
    "Desert": os.path.join(VANILLA, "Desert.tmx"),
    "Mine": os.path.join(VANILLA, "Mine.tmx"),
    "SkullCave": os.path.join(VANILLA, "SkullCave.tmx"),
    "Woods": os.path.join(SVE, "Locations", "Woods2.tmx"),
}
# Farm/FarmHouse зависят от фермы и дома; ArchaeologyHouse в SVE — .tbin (скрипт читает только .tmx).
UNCHECKED = {"Farm", "FarmHouse", "ArchaeologyHouse"}
OFFSCREEN = 500  # актёр за пределами сцены (1000 1000, -1000 -1000)


# ---------- карты ----------

class TileMap:
    def __init__(self, path):
        root = ET.parse(path).getroot()
        self.width = int(root.get("width"))
        self.height = int(root.get("height"))
        self.layers = {}
        for layer in root.findall("layer"):
            self.layers[layer.get("name")] = self._decode(layer.find("data"))
        self.passable = self._read_passable_overrides(root)

    def _decode(self, data):
        if data.get("encoding") == "csv":
            return [int(v) & 0x1FFFFFFF for v in data.text.replace("\n", "").split(",")]
        raw = base64.b64decode(data.text.strip())
        if data.get("compression") == "zlib":
            raw = zlib.decompress(raw)
        elif data.get("compression") == "gzip":
            raw = gzip.decompress(raw)
        return [v & 0x1FFFFFFF for v in struct.unpack("<%dI" % (self.width * self.height), raw)]

    def _read_passable_overrides(self, root):
        """Объекты слоя Buildings со свойством Passable или дверью (Action Door…) делают тайл проходимым."""
        tiles = set()
        for group in root.findall("objectgroup"):
            if group.get("name") != "Buildings":
                continue
            for obj in group.findall("object"):
                if any(p.get("name") == "Passable"
                       or (p.get("name") == "Action" and (p.get("value") or "").startswith("Door"))
                       for p in obj.iter("property")):
                    tiles.add((int(float(obj.get("x")) // 16), int(float(obj.get("y")) // 16)))
        return tiles

    def tile(self, layer, x, y):
        data = self.layers.get(layer)
        if data is None or not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        return data[y * self.width + x]

    def problem(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return "за краем карты"
        if self.tile("Back", x, y) == 0:
            return "пустота (нет Back)"
        if self.tile("Buildings", x, y) != 0 and (x, y) not in self.passable:
            return "стена/предмет (Buildings)"
        return None


_maps = {}


def load_map(name):
    if name in _maps:
        return _maps[name]
    path = MAP_FILES.get(name)
    _maps[name] = TileMap(path) if path and os.path.exists(path) else None
    return _maps[name]


# ---------- JSONC и разбор событий ----------

def strip_jsonc(text):
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == chr(92):
                out.append(text[i + 1])
                i += 2
                continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            i = text.index("*/", i) + 2
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def split_commands(script):
    """Делит скрипт по '/' вне кавычек."""
    parts, buf, in_q = [], [], False
    for c in script:
        if c == '"':
            in_q = not in_q
        if c == "/" and not in_q:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(c)
    if buf:
        parts.append("".join(buf).strip())
    return parts


def iter_events():
    code = os.path.join(CP_ROOT, "assets", "Code")
    for fname in sorted(os.listdir(code)):
        if not fname.endswith(".json"):
            continue
        try:
            doc = json.loads(strip_jsonc(open(os.path.join(code, fname), encoding="utf-8-sig").read()), strict=False)
        except Exception as exc:  # noqa: BLE001
            print(f"!! {fname}: не разобран JSON ({exc})")
            continue
        for change in doc.get("Changes", []) if isinstance(doc, dict) else []:
            target = change.get("Target", "")
            if not target.startswith("Data/Events/"):
                continue
            location = target.split("/")[-1]
            for key, script in (change.get("Entries") or {}).items():
                if isinstance(script, str):
                    yield fname, location, key.split("/")[0], script


# ---------- симуляция ----------

def is_posed_after(body, index, actor):
    """warp на кровать/стул с последующей позой (positionOffset/showFrame/лёжа) — намеренно."""
    for raw in body[index + 1:index + 5]:
        tokens = raw.split()
        if len(tokens) > 1 and tokens[0] in ("positionOffset", "showFrame", "animate") and tokens[1] == actor:
            return True
    return False


def validate(fname, location, event_id, script):
    issues = []
    cmds = split_commands(script)
    if len(cmds) < 3:
        return issues

    loc = location
    actors = {}
    ignore = set()

    def check(actor, x, y, what):
        if loc in UNCHECKED or x < 0 or y < 0 or x >= OFFSCREEN or y >= OFFSCREEN:
            return
        tmap = load_map(loc)
        if tmap is None:
            return
        problem = tmap.problem(x, y)
        if problem and actor not in ignore:
            issues.append(f"{what}: {actor} ({x},{y}) в {loc} — {problem}")
        elif problem and actor in ignore and problem.startswith(("за краем", "пустота")):
            issues.append(f"{what}: {actor} ({x},{y}) в {loc} — {problem} (ignoreCollisions не спасает)")

    setup = cmds[2].split()
    for i in range(0, len(setup) - 3, 4):
        try:
            name, x, y = setup[i], int(setup[i + 1]), int(setup[i + 2])
        except ValueError:
            break
        actors[name] = (x, y)
        check(name, x, y, "старт")

    body = cmds[3:]
    for index, raw in enumerate(body):
        tokens = raw.split()
        if not tokens:
            continue
        cmd = tokens[0]
        try:
            if cmd == "changeLocation" and len(tokens) > 1:
                loc = tokens[1]
            elif cmd == "ignoreCollisions" and len(tokens) > 1:
                ignore.add(tokens[1])
            elif cmd == "warp" and len(tokens) >= 4:
                name, x, y = tokens[1], int(tokens[2]), int(tokens[3])
                actors[name] = (x, y)
                if not is_posed_after(body, index, name):
                    check(name, x, y, "warp")
            elif cmd == "move" and len(tokens) >= 4 and tokens[1] in actors:
                name, dx, dy = tokens[1], int(tokens[2]), int(tokens[3])
                x, y = actors[name]
                if x < 0 or y < 0 or x >= OFFSCREEN:
                    continue
                if dx and dy:
                    issues.append(f"move: {name} {dx} {dy} — оба смещения ненулевые, ось выберет игра")
                step_x = (dx > 0) - (dx < 0)
                step_y = (dy > 0) - (dy < 0)
                for _ in range(abs(dx)):
                    x += step_x
                    check(name, x, y, f"move {dx} {dy}")
                for _ in range(abs(dy)):
                    y += step_y
                    check(name, x, y, f"move {dx} {dy}")
                actors[name] = (x, y)
        except ValueError:
            continue

    return issues


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    total, checked = 0, 0
    for fname, location, event_id, script in iter_events():
        checked += 1
        issues = validate(fname, location, event_id, script)
        # Повторы одной и той же клетки в пределах события сворачиваем.
        seen = []
        for issue in issues:
            if issue not in seen:
                seen.append(issue)
        if seen:
            total += len(seen)
            print(f"\n[{fname}] {event_id} ({location})")
            for issue in seen:
                print(f"  - {issue}")

    missing = sorted(n for n, p in MAP_FILES.items() if not os.path.exists(p))
    print(f"\nСобытий проверено: {checked}, замечаний: {total}")
    print(f"Без проверки: {', '.join(sorted(UNCHECKED))} (ферма/дом зависят от сохранения, музей SVE — .tbin)")
    if missing:
        print(f"Нет карт: {', '.join(missing)}")


if __name__ == "__main__":
    main()
