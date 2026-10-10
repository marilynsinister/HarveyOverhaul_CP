"""Общие помощники для генераторов событий (build_marriage_events.py).

Сцены пишутся списками команд, чтобы JSON-экранирование кавычек и обратных слэшей
делал json.dump, а не руками. Формат совпадает с build_arc3_events.py.
"""

CD = 'HarveyMod_CD_Global'
H = 'Harvey'


def sp(who, text):
    assert '"' not in text, text
    return f'speak {who} "{text}"'


def msg(text):
    assert '"' not in text, text
    return f'message "{text}"'


def qq(answers, branches, question=''):
    """quickQuestion: answers — список, branches — список списков команд."""
    assert len(answers) == len(branches)
    for t in answers:
        assert '#' not in t and '/' not in t
    head = f'quickQuestion {question}#' + '#'.join(answers)
    return head + ''.join('(break)' + '\\'.join(b) for b in branches)


def key(ns, eid, *conds, cooldown=True):
    """Ключ события. cooldown=False — для сцен, привязанных к дате (годовщина, день рождения)."""
    parts = [f'{ns}.{eid}', *conds, '!FestivalDay',
             f'GameStateQuery !PLAYER_HAS_SEEN_EVENT Current {ns}.{eid}']
    if cooldown:
        parts.append(f'GameStateQuery !PLAYER_HAS_CONVERSATION_TOPIC Current {CD}')
    return '/'.join(parts)


def script(music, view, actors, skip, body, ending='end'):
    cmds = [music, view, actors, 'skippable', 'setSkipActions ' + '#'.join(skip), *body,
            f'addConversationTopic {CD} 3', 'globalFade', 'viewport -1000 -1000', ending]
    for c in cmds:
        assert '/' not in c, c
    return '/'.join(cmds)


def skip_cd(*extra):
    return [f'AddConversationTopic Current {CD} 3', *extra]


def patch(log, target, entries):
    return {'LogName': log, 'Action': 'EditData', 'Target': target, 'Entries': entries}
