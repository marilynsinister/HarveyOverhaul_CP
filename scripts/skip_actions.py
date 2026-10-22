"""setSkipActions: что сделать, если игрок пропустил сцену.

setSkipActions принимает trigger actions (AddConversationTopic, AddMail, AddFriendshipPoints…), а не команды
события. После пропуска игра сама возвращает фермера туда, где сцена началась, поэтому warp/changeLocation/
faceDirection там не нужны (и не работают). complete_skip() чинит список и дописывает эффекты из тела сцены,
которые иначе потеряются: темы, письма, дружбу, предметы, квесты и `action …` вне веток quickQuestion.
"""

# Команды события → trigger action. None — команда только про сцену, при пропуске не нужна.
_EVENT_TO_ACTION = {
    'addconversationtopic': lambda a: ['AddConversationTopic', *a],
    'removeconversationtopic': lambda a: ['RemoveConversationTopic', *a],
    'friendship': lambda a: ['AddFriendshipPoints', *a],
    'additem': lambda a: ['AddItem', *a],
    'addobject': lambda a: ['AddItem', *a],
    'addquest': lambda a: ['AddQuest', *a],
    'removequest': lambda a: ['RemoveQuest', *a],
    'mail': lambda a: ['AddMail', 'Current', a[0], 'tomorrow'],
    'addmailreceived': lambda a: ['AddMail', 'Current', a[0], 'received'],
    'money': lambda a: ['AddMoney', *a],
    'action': lambda a: list(a),
}
_SCENE_ONLY = {
    'warp', 'changelocation', 'facedirection', 'positionoffset', 'ignorecollisions', 'warpout', 'viewport',
    'fade', 'globalfade', 'move', 'pause', 'emote', 'playsound', 'showframe', 'animate', 'stopanimation',
    'speak', 'message', 'end', 'jump', 'shake', 'ambientlight', 'playmusic', 'stopmusic', 'addtemporaryactor',
}


def to_action(cmd, from_skip=True):
    """Команда события или skip-действие → trigger action (строка) или None.

    from_skip=False — команда из тела сцены: берутся только команды, меняющие состояние.
    """
    tokens = cmd.split()
    if not tokens:
        return None
    name = tokens[0].lower()
    if name in _SCENE_ONLY:
        return None
    convert = _EVENT_TO_ACTION.get(name)
    if convert is None:
        if not from_skip:
            return None
        return ' '.join(tokens)  # уже trigger action (AddMail, MarkEventSeen, действия модов…)
    try:
        result = convert(tokens[1:])
    except IndexError:
        return None
    if not result:
        return None
    if name == 'action':
        return to_action(' '.join(result))  # «action RemoveConversationTopic X» → то же, что без «action»
    if result[0].lower() == 'addconversationtopic':
        result[0] = 'AddConversationTopic'
    return ' '.join(result)


def effect_key(action):
    tokens = action.split()
    name = tokens[0].lower()
    if name in ('addconversationtopic', 'removeconversationtopic', 'addquest', 'removequest', 'additem') and len(tokens) > 1:
        return name, tokens[1]
    if name == 'addmail' and len(tokens) > 2:
        return name, tokens[2]
    if name == 'addfriendshippoints' and len(tokens) > 1:
        return name, tokens[1]
    return name, ' '.join(tokens[1:])


def complete_skip(skip, body):
    """Исправленный список skip-действий: только trigger actions + эффекты тела сцены, которых в нём нет."""
    out, seen = [], set()
    for raw, from_skip in [*((a, True) for a in skip), *((c, False) for c in body)]:
        action = to_action(raw, from_skip)
        if not action:
            continue
        key = effect_key(action)
        if key in seen:
            continue
        seen.add(key)
        out.append(action)
    return out
