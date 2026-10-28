"""Validate the herbal garden's playable chain, config branches and crop atlas.

Run: python scripts/validate_herbal_garden.py
No game save or installed Mods directory is modified.
"""
import json
import re
from pathlib import Path
from PIL import Image
from validate_event_coords import strip_jsonc

ROOT = Path(__file__).resolve().parent.parent
MOD = "{{ModId}}_"
DATA = ROOT / "assets/Code/herbalGarden.json"
INK = (48, 30, 37, 255)


def dark_contour(sprite, label):
    # A coloured edge adjacent to transparency disappears against game soil.
    # Validate the saved game pixels, independently of the drawing routines.
    for y in range(sprite.height):
        for x in range(sprite.width):
            pixel = sprite.getpixel((x, y))
            if pixel[3] and any(
                not (0 <= xx < sprite.width and 0 <= yy < sprite.height)
                or not sprite.getpixel((xx, yy))[3]
                for xx, yy in ((x-1, y), (x+1, y), (x, y-1), (x, y+1))
            ):
                assert pixel == INK, (label, "broken dark contour", x, y)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f"Duplicate JSON key: {key}"
        result[key] = value
    return result


def read(path):
    return json.loads(strip_jsonc(path.read_text(encoding="utf-8-sig")),
                      object_pairs_hook=unique_pairs, strict=False)


def entries(changes, target):
    result = {}
    for change in changes:
        if change.get("Target") == target:
            for key, value in change.get("Entries", {}).items():
                assert key not in result, f"Duplicate entry in {target}: {key}"
                result[key] = value
    return result


def main():
    changes = read(DATA)["Changes"]
    root = read(ROOT / "content.json")
    assert sum(c.get("FromFile") == "assets/Code/herbalGarden.json" for c in root["Changes"]) == 1
    assert all(c.get("When", {}) in ({}, {"TraumaBackstory": "true"}) for c in changes)
    for change in changes:
        if change["Action"] == "Load":
            assert (ROOT / change["FromFile"]).is_file()

    objects = entries(changes, "Data/Objects")
    crops = entries(changes, "Data/Crops")
    shop = entries(changes, "Data/Shops")
    quests = entries(changes, "Data/Quests")
    mail = entries(changes, "Data/Mail")
    triggers = entries(changes, "Data/TriggerActions")
    recipes = {**entries(changes, "Data/CookingRecipes"), **entries(changes, "Data/CraftingRecipes")}
    assert (len(objects), len(crops), len(shop), len(quests), len(recipes)) == (10, 4, 8, 5, 4)

    icons = Image.open(ROOT / "assets/Items/herbalItems.png").convert("RGBA")
    atlas = Image.open(ROOT / "assets/Crops/herbalCrops.png").convert("RGBA")
    assert icons.size == (128, 16)
    assert atlas.size == (256, 64)
    for relative, runtime in (("Items/herbalItems.png", icons), ("Crops/herbalCrops.png", atlas)):
        source = ROOT / "art/herbal-garden/exports" / Path(relative).name
        assert Image.open(source).convert("RGBA").tobytes() == runtime.tobytes(), relative
    for image in (icons, atlas):
        assert set(image.getchannel("A").get_flattened_data()) == {0, 255}
        assert len({pixel[:3] for pixel in image.get_flattened_data() if pixel[3]}) <= 64
    for key, obj in objects.items():
        if obj.get("Texture") != "Mods/{{ModId}}/HerbalItems":
            continue  # общий сбор и страница тетради — чужие листы
        index = obj["SpriteIndex"]
        sprite = icons.crop((index * 16, 0, index * 16 + 16, 16))
        box = sprite.getbbox()
        assert box and box[0] >= 1 and box[1] >= 1 and box[2] <= 15 and box[3] <= 15, key
        dark_contour(sprite, key)

    for seed, crop in crops.items():
        assert objects[seed]["Category"] == -74 and objects[seed]["Type"] == "Seeds"
        herb = crop["HarvestItemId"]
        assert herb in objects and crop["RegrowDays"] > 0
        assert len(crop["DaysInPhase"]) == 4, "Export packs four growing phases before maturity"
        assert all(day > 0 for day in crop["DaysInPhase"])
        assert f"{sum(crop['DaysInPhase'])} дн." in objects[seed]["Description"]
        assert not crop["CountForMonoculture"] and not crop["CountForPolyculture"]
        assert shop[herb]["AvailableStock"] >= 3 and shop[herb]["AvailableStockLimit"] == "Player"
        # Сырьё в клинике — только после финала, иначе всю цепочку можно купить и сдать за день.
        assert shop[herb]["Condition"] == "PLAYER_HAS_MAIL Current " + MOD + "HerbalGardenFinished Received"
        assert shop[herb]["Price"] > objects[herb]["Price"]
        assert shop[seed]["PriceModifiers"][0]["Amount"] == 0.9
        index = crop["SpriteIndex"]
        row = []
        for frame in range(8):
            # Verified against the installed 1.6 Crop.getSourceRect, including
            # the two seed variants and the hard-coded regrowth slots 6 and 7.
            x, y = (index % 2) * 128 + frame * 16, (index // 2) * 32
            sprite = atlas.crop((x, y, x + 16, y + 32))
            box = sprite.getbbox()
            assert box and box[0] >= 1 and box[2] <= 15 and box[3] == 31, (seed, frame, box)
            dark_contour(sprite, (seed, frame))
            row.append(sprite.tobytes())
        assert row[0] == row[1], "Both seed variants must exist"
        assert row[5] == row[6] and row[6] != row[7], "Mature and picked regrowth frames"
        assert any(herb in recipe.split("/")[0] for recipe in recipes.values()), f"Unused herb: {herb}"
    print("OK: 8 icons; 4 crop rows; all phases, seed variants and regrowth coordinates; binary alpha; dark contours; export copies.")

    known_objects = dict(objects)
    for filename in ("medicalItems.json", "trustRewards.json", "eventsScars.json"):
        known_objects.update(entries(read(ROOT / "assets/Code" / filename)["Changes"], "Data/Objects"))
    for key, recipe in recipes.items():
        fields = recipe.split("/")
        ingredients = fields[0].split()
        assert len(ingredients) % 2 == 0
        for item, amount in zip(ingredients[::2], ingredients[1::2]):
            assert int(amount) > 0
            assert not item.startswith(MOD) or item in objects, (key, item)
        output, quantity = fields[2].split()
        assert output in known_objects and int(quantity) == 1
        assert "none" in fields, "Recipes must be explicitly taught, never automatic"

    start = MOD + "GardenGlass"
    # Каждый шаг — своё действие: вырастить для Харви, отнести Эвелин, отнести Гасу,
    # найти страницу у фонтана, приготовить общий сбор. Сырьё по пути не продаётся.
    expected = [
        ("ItemDelivery", "Harvey", "GlassDewberry", 3),
        ("ItemDelivery", "Evelyn", "Moonvelvet", 3),
        ("ItemDelivery", "Gus", "AmberHeartleaf", 3),
        ("LostItem", "Harvey", "NotebookPage", None),
        ("ItemDelivery", "Harvey", "GardenBlend", 1),
    ]
    order, current = [], start
    while current != "-1":
        assert current in quests and current not in order, "Missing quest or cycle"
        order.append(current)
        fields = quests[current].split("/")
        kind, npc_name, item_name, amount = expected[len(order) - 1]
        assert len(fields) == 10 and fields[0] == kind and fields[8] == "false", current
        req = fields[4].split()
        assert req[0] == npc_name and req[1] == "(O)" + MOD + item_name, current
        assert req[1].removeprefix("(O)") in known_objects
        if kind == "LostItem":
            assert objects[MOD + item_name]["Type"] == "Quest" and len(req) == 5
        else:
            assert int(req[2]) == amount
        assert int(fields[6]) > 0
        current = fields[5]
    assert len(order) == len(quests) == 5
    assert MOD + "HerbalGardenFinished Received" in quests[order[-1]]
    blend = recipes[MOD + "GardenBlendRecipe"].split("/")[0]
    assert all(MOD + herb in blend for herb in ("GlassDewberry", "Moonvelvet", "AmberHeartleaf", "SilverSeamleaf"))

    flags = {MOD + name for name in ("GardenAmberStudied", "GardenSilverStudied", "HerbalGardenFinished")}
    for text in list(mail.values()) + list(quests.values()):
        for target in re.findall(r"AddMail Current ([^\s#]+)", text):
            assert target in mail or target in flags, f"Missing letter/flag: {target}"
    for key, text in mail.items():
        for kind, body in re.findall(r"%item (\w+) (.*?)\s*%%", text):
            fields = body.split()
            if kind == "id":
                # Multiple pairs in one %item id select a RANDOM item in vanilla.
                # A single pair is required for a guaranteed quest seed reward.
                assert len(fields) == 2 and fields[0].removeprefix("(O)") in objects, key
                assert int(fields[1]) == 3
            elif kind == "quest":
                assert fields[0] == start and fields[1] == "true"
            elif kind in ("cookingRecipe", "craftingRecipe"):
                assert fields[0] in recipes
            else:
                raise AssertionError((key, kind))
    for trigger in triggers.values():
        assert trigger["Trigger"] == "DayStarted"
        assert trigger.get("MarkActionApplied", True), "Rewards must run only once"
        for action in trigger["Actions"]:
            assert action.split()[0] == "AddMail" and action.split()[2] in mail
    print("OK: 5 linked quests (3 deliveries, lost page, cooked blend); guaranteed seed mail; recipe and letter references; one-time rewards.")

    for trauma in (False, True):
        active = [c for c in changes if not c.get("When") or trauma]
        active_recipes = entries(active, "Data/CraftingRecipes")
        active_triggers = entries(active, "Data/TriggerActions")
        assert (MOD + "GardenSalveRecipe" in active_recipes) == trauma
        assert (MOD + "HerbalGardenSalve" in active_triggers) == trauma
        # Every output is the original medical object used by the C# managers.
        assert recipes[MOD + "GardenTeaRecipe"].split("/")[2] == MOD + "HerbalTea 1"
        assert recipes[MOD + "GardenBrothRecipe"].split("/")[2] == MOD + "HarveyBroth 1"
    assert "PLAYER_HAS_COOKING_RECIPE Current " + MOD + "HarveyBroth" in triggers[MOD + "HerbalGardenBroth"]["Condition"]
    assert "PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulScars.C3_ScarSalve" in triggers[MOD + "HerbalGardenSalve"]["Condition"]
    assert next(c for c in changes if c.get("Fields")).get("Priority") == "Late"
    print("OK: TraumaBackstory true/false; broth trust gate; salve scene gate; existing medical IDs preserved.")
    print("Herbal garden: all static checks passed.")


if __name__ == "__main__":
    main()
