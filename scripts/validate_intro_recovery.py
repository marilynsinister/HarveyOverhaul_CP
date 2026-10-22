"""Регрессии ранних сцен: поздний сейв, запись, отказ, пропуск и регистр погоды.

Принимает необязательный путь к CP-паку, чтобы проверить и установленную версию.
Ничего не записывает в сохранения. Игра сравнивает Weather с sunny/rainy
регистрозависимо; остальные значения — точные ID погоды (Sun, Storm и т.д.).
"""
import json
from pathlib import Path
import shlex
import sys

from validate_event_coords import strip_jsonc

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]


def read(name):
    return json.loads(strip_jsonc((ROOT / name).read_text(encoding='utf-8-sig')), strict=False)


def event(name, *files):
    matches = [(ch['Target'], key, body) for fn in files for ch in read(fn)['Changes']
               for key, body in ch.get('Entries', {}).items() if key.split('/')[0] == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]


def query(text, state):
    args = shlex.split(text)
    name, *args = args
    invert = name.startswith('!')
    name = name.lstrip('!')
    if name == 'ANY':
        result = any(query(q, state) for q in args)
    elif name == 'DAYS_PLAYED':
        result = int(args[0]) <= state['days'] <= (int(args[1]) if len(args) > 1 else 2**31 - 1)
    elif name == 'PLAYER_HAS_SEEN_EVENT':
        result = args[1] in state['seen']
    elif name == 'PLAYER_HAS_CONVERSATION_TOPIC':
        result = args[1] in state['topics']
    elif name == 'PLAYER_HAS_MAIL':
        result = args[1] in state['mail']
    else:
        raise AssertionError('Unsupported test query: ' + text)
    return not result if invert else result


def available(key, state):
    eid, *conditions = key.split('/')
    if eid in state['seen']:
        return False  # Игра сама исключает просмотренные события до проверки условий.
    for condition in conditions:
        if condition.startswith('GameStateQuery '):
            if not query(condition.removeprefix('GameStateQuery '), state):
                return False
        elif condition.startswith('Time '):
            _, start, end = condition.split()
            if not int(start) <= state['time'] <= int(end):
                return False
        elif condition.startswith('Weather '):
            weather = condition.split()[1]
            if weather == 'sunny':
                if state['weather'] in {'Rain', 'Storm', 'GreenRain'}:
                    return False
            elif weather == 'rainy':
                if state['weather'] not in {'Rain', 'Storm', 'GreenRain'}:
                    return False
            elif weather != state['weather']:
                return False
        else:
            raise AssertionError('Unsupported test precondition: ' + condition)
    return True


def main():
    source = 'assets/Code/'
    farm, walk, _ = event('eventHarveyFirstWalk', source + 'events.json')
    hospital, checkup, checkup_body = event('eventHarveyCheckup', source + 'eventsCare.json')
    invitation_location, invitation, invite_body = event('eventHarveyCheckupInvitation', source + 'introRecovery.json')
    assert farm == 'Data/Events/Farm'
    assert hospital == invitation_location == 'Data/Events/Hospital'
    assert any(ch.get('FromFile') == source + 'introRecovery.json' for ch in read('content.json')['Changes'])

    # Состояние позднего сейва со скриншота: второй визит был, короткие темы уже истекли.
    state = {'days': 52, 'time': 900, 'weather': 'Sun',
             'seen': {'eventHarveyFirstMeeting', 'eventHarveyFirstVisit', 'eventHarveySecondVisit'},
             'topics': set(), 'mail': set()}
    assert available(walk, state), 'Late-save walk should be available on a dry morning'
    assert not available(walk, {**state, 'weather': 'Rain'})
    assert not available(walk, {**state, 'time': 1300})
    assert not available(walk, {**state, 'seen': state['seen'] | {'eventHarveyFirstWalk'}})
    for outcome in ('Agree', 'Neutral', 'Refused'):
        assert not available(walk, {**state, 'topics': {'topicHarveySecondVisit' + outcome}})

    clinic = {**state, 'time': 1500}
    assert not available(checkup, clinic), 'Exam must still need consent'
    assert available(invitation, clinic), 'An expired or missing booking must be recoverable'
    booked = {**clinic, 'mail': {'HarveyIntro_CheckupAgreed'}}
    assert available(checkup, booked), 'Permanent booking must survive expired dialogue topics'
    assert not available(invitation, booked)
    legacy = {**clinic, 'topics': {'topicAgreedCheckup'}}
    assert available(checkup, legacy), 'Old active booking must still work'
    assert not available(invitation, legacy)
    deferred = {**clinic, 'topics': {'topicRefusedCheckup'}}
    assert not available(invitation, deferred), 'Refusal must postpone the invitation'
    completed = {**clinic, 'seen': clinic['seen'] | {'eventHarveyCheckup'}}
    assert not available(checkup, completed) and not available(invitation, completed)
    assert not available(checkup, {**booked, 'time': 1300})
    assert 'HarveyExam_CheckupStopped' in checkup_body

    # Пропуск приглашения не считается согласием; оба ответа меняют только свой исход.
    commands = invite_body.split('/')
    skip = next(c.removeprefix('setSkipActions ') for c in commands if c.startswith('setSkipActions '))
    assert skip == 'AddConversationTopic topicRefusedCheckup 7'
    question = next(c for c in commands if c.startswith('quickQuestion '))
    head, agree, refuse = question.split('(break)')
    assert len(head.split('#')[1:]) == 2
    assert 'action AddMail Current HarveyIntro_CheckupAgreed Received' in agree
    assert 'HarveyIntro_CheckupAgreed' not in refuse and 'topicAgreedCheckup' not in refuse
    assert 'addConversationTopic topicRefusedCheckup 7' in refuse

    care = read(source + 'eventsCare.json')
    first_meeting_forks = [ch['Entries']['declineFood'] for ch in care['Changes'] if 'declineFood' in ch.get('Entries', {})]
    assert len(first_meeting_forks) == 1
    assert 'question fork1 "#Согласиться на осмотр#Отказаться"' in first_meeting_forks[0]
    assert 'action AddMail Current HarveyIntro_CheckupAgreed Received' in first_meeting_forks[0]

    triggers = [v for ch in read(source + 'introRecovery.json')['Changes']
                if ch['Target'] == 'Data/TriggerActions' for v in ch['Entries'].values()]
    keep = next(t for t in triggers if t['Id'].endswith('_KeepCheckupConsent'))
    rearm = next(t for t in triggers if t['Id'].endswith('_OfferCheckupAgain'))
    assert query(keep['Condition'].replace(', ', ',').split(',')[0], legacy)
    assert all(query(q, legacy) for q in keep['Condition'].split(', '))
    assert not all(query(q, clinic) for q in keep['Condition'].split(', '))
    for test_state, expected in [
        ({**clinic, 'seen': clinic['seen'] | {'eventHarveyCheckupInvitation'}}, True),
        ({**deferred, 'seen': clinic['seen'] | {'eventHarveyCheckupInvitation'}}, False),
        ({**completed, 'seen': completed['seen'] | {'eventHarveyCheckupInvitation'}}, False),
        ({**booked, 'seen': clinic['seen'] | {'eventHarveyCheckupInvitation'}}, False),
    ]:
        assert all(query(q, test_state) for q in rearm['Condition'].split(', ')) == expected
    assert rearm['Actions'] == ['MarkEventSeen Current eventHarveyCheckupInvitation false']
    assert all(t['Trigger'] == 'DayStarted' and not t['MarkActionApplied'] for t in triggers)

    # Не дать генераторам вернуть ту же ошибку в других сюжетных ветках.
    import re
    invalid = {'Sunny', 'Rainy', 'sun', 'rain', 'storm', 'wind', 'snow', 'greenrain'}
    checked = 0
    for path in (ROOT / source).rglob('*.json'):
        for weather in re.findall(r'(?<!\w)Weather (\w+)', path.read_text(encoding='utf-8-sig')):
            assert weather not in invalid, (path, weather)
            checked += 1
    print(f'Intro recovery: all checks passed. {checked} weather conditions checked.')


if __name__ == '__main__':
    main()
