import json
from pathlib import Path

def strip_comments(text: str) -> str:
    out, i, in_str, escape = [], 0, False, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)

root = Path(__file__).resolve().parents[1]
orig = json.loads(strip_comments((root / "assets/Code/dialoguesHarvey.json").read_text(encoding="utf-8")))
oc = sum(len(c.get("Entries", {})) for c in orig["Changes"] if c.get("Action") == "EditData")
split = 0
for p in (root / "assets/Code/dialogues").glob("harvey_*.json"):
    d = json.loads(strip_comments(p.read_text(encoding="utf-8")))
    split += sum(len(c.get("Entries", {})) for c in d["Changes"] if c.get("Action") == "EditData")
print("orig", oc, "split", split, "match", oc == split)
