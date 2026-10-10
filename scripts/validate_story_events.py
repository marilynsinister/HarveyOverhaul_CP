"""Статическая проверка сгенерированных сюжетных событий (арка 3, свидание, брак).

Проверяет то, что ломает сцену молча, без ошибки в SMAPI:
  * команды не содержат '/' внутри, кавычки speak/message закрыты, сцена заканчивается end;
  * в quickQuestion столько веток, сколько ответов;
  * каждый актёр из warp/move/speak/emote/faceDirection объявлен в строке актёров;
  * GameStateQuery-условия существуют в игре (список PLAYER_* из Stardew Valley.dll);
  * PLAYER_HAS_SEEN_EVENT ссылается на существующее событие мода;
  * AddMail-письма, у которых нет текста, — только флаги из ALLOWED_FLAGS;
  * у каждой темы addConversationTopic есть реплика хотя бы у одного NPC;
  * темы триггеров TriggerActions тоже имеют реплики.
Запуск:  python scripts/validate_story_events.py [путь к игре]
Код выхода 1 — если есть ошибки.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, 'assets', 'Code')
GAME = sys.argv[1] if len(sys.argv) > 1 else r'D:\Games\Steam\steamapps\common\Stardew Valley'

EVENT_FILES = ['eventsArc3.json', 'eventsMarriage.json', 'eventsAdult.json']
TRIGGER_FILES = ['triggersArc3Aftermath.json', 'triggersDate.json']
# Флаги-«письма» без текста: их читают условия и диалоги, в почтовый ящик они не попадают.
ALLOWED_FLAGS = {'HarveyArc3_Confessed', 'HarveyArc3_ConfessionPending', 'HarveyArc3_Graduated'}
# Темы-служебки без реплик.
SILENT_TOPICS = {'HarveyMod_CD_Global'}

errors, warnings = [], []


def strip_comments(text):
    out, i, in_str = [], 0, False
    while i < len(text):
        c = text[i]
        if in_str:
            out.append(c)
            if c == '\\':
                out.append(text[i + 1]); i += 2; continue
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True; out.append(c)
        elif text.startswith('//', i):
            while i < len(text) and text[i] != '\n':
                i += 1
            continue
        elif text.startswith('/*', i):
            i = text.index('*/', i) + 2; continue
        else:
            out.append(c)
        i += 1
    s = ''.join(out)
    return re.sub(r',(\s*[}\]])', r'\1', s)


def load(name):
    with open(os.path.join(CODE, name), encoding='utf-8') as f:
        return json.loads(strip_comments(f.read()))


def all_entries(target_prefix):
    """Все ключи из EditData-патчей с Target, начинающимся на prefix, по всем json мода."""
    found = {}
    for dirpath, _, files in os.walk(CODE):
        for fn in files:
            if not fn.endswith('.json'):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, encoding='utf-8') as f:
                    data = json.loads(strip_comments(f.read()))
            except (ValueError, IndexError):
                continue  # многострочные событийные строки CP — не строгий JSON; там нужных ключей нет
            for ch in data.get('Changes', []) if isinstance(data, dict) else []:
                t = ch.get('Target', '')
                if t.startswith(target_prefix):
                    for k in (ch.get('Entries') or {}):
                        found.setdefault(k, set()).add(t)
    return found


def game_queries():
    dll = os.path.join(GAME, 'Stardew Valley.dll')
    if not os.path.exists(dll):
        warnings.append(f'нет {dll} — GameStateQuery не проверены')
        return None
    data = open(dll, 'rb').read()
    return {m.decode() for m in re.findall(rb'(?:PLAYER|LOCATION|WORLD|SEASON|DAY|RANDOM|TIME|WEATHER|ANY|IS)_?[A-Z_]{0,40}', data)}


def split_commands(script):
    return script.split('/')


def check_event(eid, script, actors_known_ids):
    cmds = split_commands(script)
    if not cmds[-1].startswith('end'):
        errors.append(f'{eid}: последняя команда не end ({cmds[-1]!r})')
    actors = {'farmer'}
    parts = cmds[2].split()
    for i in range(0, len(parts), 4):
        actors.add(parts[i])
    used = []
    for c in cmds:
        for piece in re.split(r'\(break\)|\\', c):
            piece = piece.strip()
            if piece.count('"') % 2:
                errors.append(f'{eid}: незакрытая кавычка: {piece[:60]}')
            m = re.match(r'(warp|move|speak|emote|faceDirection|showFrame)\s+(\S+)', piece)
            if m:
                used.append(m.group(2))
        if c.startswith('quickQuestion'):
            head, *branches = c.split('(break)')
            answers = head.split('#')[1:]
            if len(answers) != len(branches):
                errors.append(f'{eid}: quickQuestion — ответов {len(answers)}, веток {len(branches)}')
    for who in used:
        if who not in actors:
            errors.append(f'{eid}: актёр {who} не объявлен в «{cmds[2]}»')
    topics = re.findall(r'addConversationTopic (\S+)', script)
    mails = re.findall(r'AddMail Current (\S+)', script)
    return topics, mails


def main():
    queries = game_queries()
    mail = all_entries('Data/Mail')
    dialogue = all_entries('Characters/Dialogue/')
    event_ids = set()
    events = []
    for fn in EVENT_FILES:
        for ch in load(fn)['Changes']:
            if not ch['Target'].startswith('Data/Events/'):
                continue
            for k, v in ch['Entries'].items():
                eid = k.split('/')[0]
                event_ids.add(eid)
                events.append((fn, ch['Target'], k, v))

    # события, на которые ссылаются, могут жить и в старых файлах
    seen_refs = set()
    topics_all, mails_all = set(), set()
    for fn, target, k, v in events:
        eid = k.split('/')[0]
        for cond in k.split('/')[1:]:
            if cond.startswith('GameStateQuery'):
                body = cond[len('GameStateQuery'):].strip()
                # ANY "q1" "q2" — проверяем каждый подзапрос; иначе — первое слово.
                subs = re.findall(r'"([^"]+)"', body) if body.startswith('ANY') else [body]
                for sub in subs:
                    q = sub.split()[0].lstrip('!')
                    if queries is not None and q not in queries:
                        errors.append(f'{eid}: неизвестный GameStateQuery {q}')
                seen_refs.update(re.findall(r'PLAYER_HAS_SEEN_EVENT Current (\S+?)"?(?:\s|$)', cond))
        topics, mails = check_event(eid, v, event_ids)
        topics_all.update(topics)
        mails_all.update(mails)
        skip = re.search(r'setSkipActions ([^/]*)', v)
        if skip:
            topics_all.update(re.findall(r'AddConversationTopic Current (\S+)', skip.group(1)))
            mails_all.update(re.findall(r'AddMail Current (\S+)', skip.group(1)))

    all_event_text = ''
    for dirpath, _, files in os.walk(CODE):
        for fn in files:
            if fn.endswith('.json'):
                all_event_text += open(os.path.join(dirpath, fn), encoding='utf-8').read()
    for ref in seen_refs:
        if ref not in event_ids and ref not in all_event_text:
            errors.append(f'PLAYER_HAS_SEEN_EVENT ссылается на неизвестное событие {ref}')

    for m in sorted(mails_all):
        if m not in mail and m not in ALLOWED_FLAGS:
            errors.append(f'AddMail {m}: нет текста в Data/Mail и не в списке флагов')

    for fn in TRIGGER_FILES:
        for ch in load(fn)['Changes']:
            for tid, t in ch['Entries'].items():
                for a in t.get('Actions', []):
                    m = re.match(r'AddConversationTopic (\S+)', a)
                    if m:
                        topics_all.add(m.group(1))
                    m = re.match(r'AddMail Current (\S+)', a)
                    if m and m.group(1) not in mail:
                        errors.append(f'{tid}: письмо {m.group(1)} без текста')

    for t in sorted(topics_all - SILENT_TOPICS):
        if t not in dialogue:
            warnings.append(f'тема {t}: ни у одного NPC нет реплики')

    print(f'событий: {len(events)}, тем: {len(topics_all)}, писем/флагов: {len(mails_all)}')
    for w in warnings:
        print('WARN ', w)
    for e in errors:
        print('ERROR', e)
    print('OK' if not errors else f'{len(errors)} ошибок')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
