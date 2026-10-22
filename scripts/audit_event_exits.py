"""
Аудит выхода из событий и пропуска (skip) — все события из файлов, подключённых в content.json.

Что проверяется:
  1. setSkipActions — это trigger actions (AddConversationTopic, AddMail, AddFriendshipPoints…),
     а не команды события. warp/changeLocation/faceDirection/friendship/«action X» там не выполняются:
     игра пишет ошибку в лог, а эффект теряется. → HIGH
  2. Пропускаемое событие меняет состояние (тема, письмо, дружба, предмет, action) вне веток выбора,
     но setSkipActions этого не повторяет: при пропуске эффект теряется. → MEDIUM
  3. Событие уходит в другую локацию (changeLocation) и заканчивается простым `end`/`end dialogue`:
     после сцены игра вернёт фермера туда, где событие началось. Обычно это и нужно, но стоит знать. → INFO
  4. После пропуска игра всегда возвращает фермера на место старта: `end position`/`end warpOut` при skip
     не выполняются. Это не ошибка, просто учтено в п. 3.

Запуск:  python -I scripts/audit_event_exits.py   →  docs/event-exit-audit.md
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from skip_actions import complete_skip, effect_key, to_action  # noqa: E402
from validate_event_coords import CP_ROOT, iter_event_entries, split_commands  # noqa: E402

OUT = os.path.join(CP_ROOT, "docs", "event-exit-audit.md")

# Trigger actions игры 1.6 (без учёта регистра). Действия модов узнаются по точке/подчёркиванию в имени.
TRIGGER_ACTIONS = {name.lower() for name in (
    "AddBuff RemoveBuff AddConversationTopic RemoveConversationTopic AddCookingRecipe AddCraftingRecipe "
    "AddFriendshipPoints AddItem RemoveItem AddMail RemoveMail AddMoney AddQuest RemoveQuest AddSpecialOrder "
    "RemoveSpecialOrder If IncrementStat MarkActionApplied MarkCookingRecipeKnown MarkCraftingRecipeKnown "
    "MarkEventSeen MarkQuestionAnswered MarkSongHeard Null RemoveTemporaryAnimatedSprites SetNpcInvisible "
    "SetNpcVisible"
).split()}

# Чем заменить команду события в setSkipActions.
SKIP_REPLACEMENT = {
    "friendship": "AddFriendshipPoints <NPC> <очки>",
    "action": "само действие без слова «action»",
    "addconversationtopic": "AddConversationTopic (уже верно, регистр не важен)",
    "additem": "AddItem (уже верно)",
    "mail": "AddMail Current <id> tomorrow",
    "addmailreceived": "AddMail Current <id> received",
}
MOVEMENT = {"warp", "changelocation", "faceDirection".lower(), "positionoffset", "ignorecollisions", "warpout",
            "viewport", "fade", "globalfade", "move"}


def is_trigger_action(name):
    low = name.lower()
    return low in TRIGGER_ACTIONS or "." in name or "_" in name


def audit(fname, location, key, script):
    eid = key.split("/")[0]
    cmds = split_commands(script)
    body = cmds[3:] if len(cmds) > 3 else []
    findings = []

    skippable = any(c.split()[:1] == ["skippable"] for c in body)
    skip_line = next((c for c in body if c.startswith("setSkipActions")), None)
    skip_actions = []
    if skip_line:
        skip_actions = [a.strip() for a in skip_line[len("setSkipActions"):].split("#") if a.strip()]

    bad = [a for a in skip_actions if not is_trigger_action(a.split()[0])]
    if bad:
        hints = sorted({SKIP_REPLACEMENT.get(a.split()[0].lower(), "убрать: при пропуске не выполняется")
                        for a in bad if a.split()[0].lower() not in MOVEMENT}
                       | ({"warp/changeLocation/faceDirection — убрать: после skip игра сама вернёт фермера на старт"}
                          if any(a.split()[0].lower() in MOVEMENT for a in bad) else set()))
        findings.append(("HIGH", f"в setSkipActions не trigger actions: `{'#'.join(bad)}`", "; ".join(hints)))

    if skippable:
        # Та же логика, что у генераторов и fix_skip_actions.py: чего нет в skip, но есть в теле сцены.
        rest = [c for c in body if c != skip_line]
        have = {effect_key(a) for a in (to_action(s) for s in skip_actions) if a}
        lost = [a for a in complete_skip(skip_actions, rest) if effect_key(a) not in have]
        if lost:
            findings.append(("MEDIUM", "при пропуске теряется: " + ", ".join(lost),
                             "добавить в setSkipActions (python -I scripts/fix_skip_actions.py)"))

    moved = [c.split()[1] for c in body if c.startswith("changeLocation ") and len(c.split()) > 1]
    last = next((c for c in reversed(body) if c.split()[:1] == ["end"]), "")
    end_kind = (last.split() + ["", ""])[1]
    if moved and moved[-1] != location and end_kind in ("", "dialogue"):
        findings.append(("INFO", f"сцена уходит в {moved[-1]}, конец `{last[:40]}` — фермер вернётся в {location}",
                         "если по сюжету она остаётся там — `end position X Y`"))

    return eid, findings


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows, total = [], 0
    for fname, location, key, script in iter_event_entries():
        total += 1
        eid, findings = audit(fname, location, key, script)
        for risk, what, fix in findings:
            rows.append((risk, fname, eid, location, what, fix))
    order = {"HIGH": 0, "MEDIUM": 1, "INFO": 2}
    rows.sort(key=lambda r: (order[r[0]], r[1], r[2]))

    def esc(s):
        return s.replace("|", "\\|").replace("\n", " ")

    counts = {k: sum(1 for r in rows if r[0] == k) for k in order}
    lines = [
        "# Аудит выхода из событий и пропуска сцен",
        "",
        f"Сгенерировано `scripts/audit_event_exits.py` {datetime.date.today():%Y-%m-%d}. "
        f"Событий: {total} (все файлы, подключённые в content.json).",
        "",
        f"HIGH: {counts['HIGH']}, MEDIUM: {counts['MEDIUM']}, INFO: {counts['INFO']}.",
        "",
        "- **HIGH** — в `setSkipActions` команды события вместо trigger actions: при пропуске не выполняются.",
        "- **MEDIUM** — пропуск сцены теряет тему, письмо, дружбу или предмет.",
        "- **INFO** — сцена уходит в другую локацию и кончается простым `end`: фермер вернётся на старт.",
        "",
        "| Risk | Файл | Событие | Локация | Что | Как исправить |",
        "|------|------|---------|---------|-----|---------------|",
    ]
    lines += [f"| {r[0]} | `{r[1]}` | `{esc(r[2])}` | {r[3]} | {esc(r[4])} | {esc(r[5])} |" for r in rows]
    if not rows:
        lines.append("| — | — | — | — | замечаний нет | — |")
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Событий: {total}; HIGH {counts['HIGH']}, MEDIUM {counts['MEDIUM']}, INFO {counts['INFO']} → {OUT}")
    for r in rows:
        if r[0] != "INFO":
            print(f"  {r[0]} {r[1]} {r[2]}: {r[4][:160]}")


if __name__ == "__main__":
    main()
