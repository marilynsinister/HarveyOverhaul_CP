"""
Проверка координат событий по реальным картам (SVE, Alchemistry Hospital, ванильные tmx).

Прогоняет команды каждого события: стартовые позиции, warp, move (с промежуточными клетками),
changeLocation, ignoreCollisions — и сообщает, где актёр встаёт или проходит через стену/пустоту.
Farm и FarmHouse проверяются на нескольких вариантах карты (тип фермы, уровень дома, брак).

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
MODS = sys.argv[1] if __name__ == "__main__" and len(sys.argv) > 1 else r"D:\Games\Steam\steamapps\common\Stardew Valley\Mods"
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
    "Custom_ShearwaterBridge": os.path.join(SVE, "NewLocations", "ShearwaterBridge.tbin"),
    "Custom_GrampletonFields_Small": os.path.join(SVE, "NewLocations", "GrampletonFields_Small.tbin"),
    "HarveyBalloon": os.path.join(os.path.dirname(MODS), "Content (unpacked)", "Maps", "HarveyBalloon.tmx"),
    "Desert": os.path.join(VANILLA, "Desert.tmx"),
    "Mine": os.path.join(VANILLA, "Mine.tmx"),
    "SkullCave": os.path.join(VANILLA, "SkullCave.tmx"),
    "Woods": os.path.join(SVE, "Locations", "Woods2.tmx"),
    "ArchaeologyHouse": os.path.join(SVE, "Locations", "ArchaeologyHouse.tbin"),
    **{name: os.path.join(CP_ROOT, 'assets', 'Maps', name + '.tmx') for name in (
        'HarveyCelebrationRoom', 'HarveyZuzuSquare', 'HarveyZuzuCafe',
        'HarveyZuzuBooks', 'HarveyZuzuCampus', 'HarveyZuzuInn')},
}

# Ферма и дом зависят от сохранения: событие проверяется на каждом варианте карты.
# Для Farm подставляются значения токенов HO_Farm* из content.json (обычная ферма / Frontier Farm).
UNPACKED = os.path.join(os.path.dirname(MODS), "Content (unpacked)", "Maps")
FRONTIER = os.path.join(MODS, "Frontier Farm", "[CP] Frontier Farm", "Assets", "Maps", "FrontierFarm.tmx")
FARM_VARIANTS = [
    ("стандартная ферма", os.path.join(UNPACKED, "Farm.tmx"), None),
    ("Frontier Farm", FRONTIER, "FrontierFarm"),
]
# До брака дом может быть любого уровня; в браке — минимум первое улучшение (с комнатой супруга).
# С уровня 2 карта больше, и игра сама сдвигает координаты событий (FarmHouse.eventPositionTileOffset):
# события пишутся в координатах дома ур. 1, сдвиг — разница между входными дверями (9,12 → 27,31).
FARMHOUSE_VARIANTS = [
    ("дом ур. 0", os.path.join(UNPACKED, "FarmHouse.tmx"), False, (0, 0)),
    ("дом ур. 1", os.path.join(UNPACKED, "FarmHouse1.tmx"), False, (0, 0)),
    ("дом ур. 2", os.path.join(UNPACKED, "FarmHouse2.tmx"), False, (18, 19)),
    ("дом ур. 1, брак", os.path.join(UNPACKED, "FarmHouse1_marriage.tmx"), True, (0, 0)),
    ("дом ур. 2, брак", os.path.join(UNPACKED, "FarmHouse2_marriage.tmx"), True, (18, 19)),
]
MARRIED_HINT = re.compile(r"Married|Marriage|Rotation|Adult|Spouse|Father|Family|Anniversary", re.I)

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


class TbinMap(TileMap):
    """Бинарная карта xTile (tBIN10). Хранит только «есть тайл / нет» и свойства Passable/Door."""

    def __init__(self, path):
        self._buf = open(path, "rb").read()
        self._pos = 0
        if self._read(6) != b"tBIN10":
            raise ValueError(f"{path}: не tBIN10")
        self._string()  # id
        self._string()  # description
        self._properties()
        for _ in range(self._int()):  # tilesheets
            self._string(); self._string(); self._string()
            self._read(4 * 8)
            self._properties()
        self.layers = {}
        self.passable = set()
        self.width = self.height = 0
        for _ in range(self._int()):
            name = self._string()
            self._read(1)  # visible
            self._string()
            width, height = self._int(), self._int()
            self._read(8)  # tile size
            self._properties()
            data = [0] * (width * height)
            for y in range(height):
                x = 0
                while x < width:
                    kind = self._read(1)
                    if kind == b"T":
                        self._string()
                    elif kind == b"N":
                        x += self._int()
                    elif kind == b"S":
                        index = self._int()
                        self._read(1)
                        props = self._properties()
                        data[y * width + x] = index + 1
                        self._mark_passable(name, x, y, props)
                        x += 1
                    elif kind == b"A":
                        self._int()  # interval
                        frames, first = self._int(), 0
                        done = 0
                        while done < frames:
                            sub = self._read(1)
                            if sub == b"T":
                                self._string()
                                continue
                            index = self._int()
                            self._read(1)
                            self._properties()
                            first = first or index + 1
                            done += 1
                        props = self._properties()
                        data[y * width + x] = first or 1
                        self._mark_passable(name, x, y, props)
                        x += 1
                    else:
                        raise ValueError(f"{path}: неизвестный тип тайла {kind!r} в слое {name}")
            self.layers[name] = data
            if name == "Back":
                self.width, self.height = width, height

    def _mark_passable(self, layer, x, y, props):
        if layer == "Buildings" and ("Passable" in props or str(props.get("Action", "")).startswith("Door")):
            self.passable.add((x, y))

    def _read(self, n):
        chunk = self._buf[self._pos:self._pos + n]
        self._pos += n
        return chunk

    def _int(self):
        return struct.unpack("<i", self._read(4))[0]

    def _string(self):
        return self._read(self._int()).decode("utf-8", "replace")

    def _properties(self):
        props = {}
        for _ in range(self._int()):
            key = self._string()
            kind = self._read(1)[0]
            if kind == 0:
                value = self._read(1)[0] != 0
            elif kind == 1:
                value = self._int()
            elif kind == 2:
                value = struct.unpack("<f", self._read(4))[0]
            else:
                value = self._string()
            props[key] = value
        return props


class OffsetMap:
    """Карта, к координатам которой игра прибавляет сдвиг события."""

    def __init__(self, base, offset):
        self.base, self.dx, self.dy = base, offset[0], offset[1]

    @staticmethod
    def wrap(base, offset):
        return base if base is None or offset == (0, 0) else OffsetMap(base, offset)

    def problem(self, x, y):
        return self.base.problem(x + self.dx, y + self.dy)


_maps = {}


def load_path(path):
    if path not in _maps:
        if not path or not os.path.exists(path):
            _maps[path] = None
        else:
            _maps[path] = TbinMap(path) if path.lower().endswith(".tbin") else TileMap(path)
    return _maps[path]


def load_map(name):
    return load_path(MAP_FILES.get(name))


def read_tokens(prefix, when_key):
    """Токены prefix* из content.json: {None: по умолчанию, значение when_key: с условием}."""
    doc = json.loads(strip_jsonc(open(os.path.join(CP_ROOT, "content.json"), encoding="utf-8-sig").read()), strict=False)
    tokens = {None: {}}
    for token in doc.get("DynamicTokens", []):
        if not token["Name"].startswith(prefix):
            continue
        farm = (token.get("When") or {}).get(when_key)
        tokens.setdefault(farm, {})[token["Name"]] = token["Value"]
    for farm, values in tokens.items():
        if farm is not None:
            tokens[farm] = {**tokens[None], **values}
    return tokens


def map_variants(location, fname, event_id):
    """(подпись, карта, подстановка токенов) — на чём проверять событие."""
    if location == "Farm":
        tokens = read_tokens("HO_Farm", "FarmType")
        return [(label, load_path(path), tokens.get(farm, tokens[None])) for label, path, farm in FARM_VARIANTS]
    if location == "FarmHouse":
        married = bool(MARRIED_HINT.search(fname) or MARRIED_HINT.search(event_id))
        tokens = read_tokens("HO_Home", "FarmhouseUpgrade")
        return [(label, OffsetMap.wrap(load_path(path), offset), tokens.get(label.split()[2].rstrip(","), tokens[None]))
                for label, path, needs_marriage, offset in FARMHOUSE_VARIANTS if needs_marriage == married]
    return [("", load_map(location), {})]


def apply_tokens(script, tokens):
    for name, value in tokens.items():
        script = script.replace("{{" + name + "}}", value)
    return script


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


def read_jsonc(path):
    with open(path, encoding="utf-8-sig") as source:
        return json.loads(strip_jsonc(source.read()), strict=False)


def included_files():
    """Файлы, которые реально подключает content.json (Include рекурсивно), в порядке подключения."""
    seen, order = set(), []

    def walk(rel):
        doc = read_jsonc(os.path.join(CP_ROOT, rel))
        for change in doc.get("Changes", []) if isinstance(doc, dict) else []:
            if change.get("Action") != "Include":
                continue
            for part in str(change.get("FromFile", "")).split(","):
                part = part.strip().replace("\\", "/")
                if part and part not in seen:
                    seen.add(part)
                    order.append(part)
                    walk(part)

    walk("content.json")
    return order


def iter_event_entries():
    """(файл, локация, полный ключ с условиями, скрипт) для событий из подключённых файлов."""
    for rel in included_files():
        fname = os.path.basename(rel)
        try:
            doc = read_jsonc(os.path.join(CP_ROOT, rel))
        except Exception as exc:  # noqa: BLE001
            print(f"!! {fname}: не разобран JSON ({exc})")
            continue
        for change in doc.get("Changes", []) if isinstance(doc, dict) else []:
            target = change.get("Target", "")
            if not target.startswith("Data/Events/"):
                continue
            for part in target.split(','):
                location = part.strip().split("/")[-1]
                for key, script in (change.get("Entries") or {}).items():
                    if isinstance(script, str):
                        yield fname, location, key, script


def iter_events():
    for fname, location, key, script in iter_event_entries():
        yield fname, location, key.split("/")[0], script


# ---------- симуляция ----------

def is_posed_after(body, index, actor):
    """warp на кровать/стул с последующей позой (positionOffset/showFrame/лёжа) — намеренно."""
    for raw in body[index + 1:index + 5]:
        tokens = raw.split()
        if len(tokens) > 1 and tokens[0] in ("positionOffset", "showFrame", "animate") and tokens[1] == actor:
            return True
    return False


def validate(fname, location, event_id, script, start_map=None):
    issues = []
    cmds = split_commands(script)
    if len(cmds) < 3:
        return issues

    loc = location
    actors = {}
    ignore = set()

    def check(actor, x, y, what, after_event=False):
        if x < 0 or y < 0 or x >= OFFSCREEN or y >= OFFSCREEN:
            return
        tmap = start_map if loc == location else map_variants(loc, fname, event_id)[0][1]
        if tmap is None:
            return
        problem = tmap.problem(x, y)
        if problem and after_event:
            # После сцены фермер ходит сам: ignoreCollisions и поза на кровати уже не действуют.
            issues.append(f"{what}: {actor} ({x},{y}) в {loc} — {problem} (после сцены застрянет)")
        elif problem and actor not in ignore:
            issues.append(f"{what}: {actor} ({x},{y}) в {loc} — {problem}")
        elif problem and actor in ignore and problem.startswith(("за краем", "пустота")):
            issues.append(f"{what}: {actor} ({x},{y}) в {loc} — {problem} (ignoreCollisions не спасает)")

    setup = cmds[2].split()
    for i in range(0, len(setup) - 3, 4):
        try:
            name, x, y = setup[i], int(setup[i + 1]), int(setup[i + 2])
        except ValueError:
            break
        if not (name == "farmer" or name.startswith("farmer") or name[:1].isupper()):
            break  # третье поле — уже команда (ambientLight 150 150 170 и т.п.), актёров в заголовке нет
        actors[name] = (x, y)
        check(name, x, y, "старт")

    body = cmds[3:]
    for index, raw in enumerate(body):
        tokens = raw.split()
        if not tokens:
            continue
        cmd = tokens[0]
        try:
            if cmd in ("changeLocation", "changeToTemporaryMap") and len(tokens) > 1:
                loc = tokens[1]
            elif cmd == "ignoreCollisions" and len(tokens) > 1:
                ignore.add(tokens[1])
            elif cmd == "addTemporaryActor" and len(tokens) >= 7:
                name = tokens[9] if len(tokens) > 9 else tokens[1]
                x, y = int(tokens[4]), int(tokens[5])
                actors[name] = (x, y)
                check(name, x, y, "addTemporaryActor")
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
            elif cmd == "end" and len(tokens) >= 4 and tokens[1] == "position":
                check("farmer", int(tokens[2]), int(tokens[3]), "end position", after_event=True)
        except ValueError:
            continue

    return issues


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    total, checked = 0, 0
    for fname, location, event_id, script in iter_events():
        checked += 1
        issues = []
        for label, tmap, tokens in map_variants(location, fname, event_id):
            suffix = f" [{label}]" if label else ""
            if tmap is None and label:
                issues.append(f"нет карты для варианта «{label}»")
                continue
            issues += [issue + suffix for issue in validate(fname, location, event_id, apply_tokens(script, tokens), tmap)]
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
    print("Farm — стандартная ферма и Frontier Farm; FarmHouse — дом ур. 0–2, в браке ур. 1–2 с комнатой супруга")
    if missing:
        print(f"Нет карт: {', '.join(missing)}")


if __name__ == "__main__":
    main()
