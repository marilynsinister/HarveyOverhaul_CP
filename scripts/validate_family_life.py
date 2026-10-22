"""Проверки доступности семейных сцен, предметов и однократных наград без изменения сохранений."""
import json
import re
from pathlib import Path

from PIL import Image
from validate_event_coords import strip_jsonc

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(strip_jsonc(path.read_text(encoding='utf-8-sig')), strict=False)


def entries(changes, target):
    result = {}
    for change in changes:
        if change.get('Target') == target:
            for key, value in change['Entries'].items():
                assert key not in result, f'Duplicate entry: {target}: {key}'
                result[key] = value
    return result


def main():
    root = read(ROOT / 'content.json')
    changes = read(ROOT / 'assets/Code/familyLife.json')['Changes']
    includes = [ch for ch in root['Changes'] if ch.get('FromFile') == 'assets/Code/familyLife.json']
    assert len(includes) == 1 and includes[0]['When']['HasMod'] == 'marilynsinister.HarveyOverhaul.Core'
    events = [(ch, key, value) for ch in changes if ch.get('Target', '').startswith('Data/Events/')
              for key, value in ch['Entries'].items()]
    assert len(events) == 7
    family = [(ch, key, value) for ch, key, value in events if key.startswith('HarveyOverhaulFamily.')]
    assert len(family) == 3
    for change, key, body in family:
        assert change['When']['ArendEnabled'] == 'true'
        assert 'PLAYER_NPC_RELATIONSHIP Current Harvey Married' in key
        assert 'PLAYER_HAS_MAIL Current HarveyFamily_ToddlerReady Received' in key
        assert 'PLAYER_HAS_SEEN_EVENT Current HarveyOverhaulArend.A1_Arrival' in key
        assert body.count('addTemporaryActor HarveyFamilyChild ') == 1
        assert body.split('/')[2].find('Arend ') >= 0

    later = [(ch, key, body) for ch, key, body in events if key.startswith('HarveyOverhaulAnniversary.A3_')]
    assert len(later) == 2 and later[0][1] == later[1][1]
    assert {ch['When']['HO_AnniversaryFamily'] for ch, _, _ in later} == {'true', 'false'}
    token = [t for t in root['DynamicTokens'] if t['Name'] == 'HO_AnniversaryFamily']
    assert len(token) == 2 and token[0]['Value'] == 'false' and 'When' not in token[0]
    assert token[1]['When'] == {'ArendEnabled': 'true', 'HasFlag': 'HarveyFamily_ToddlerReady',
                               'HasSeenEvent': 'HarveyOverhaulArend.A1_Arrival'}
    for change, _, body in later:
        assert ('addTemporaryActor' in body) == (change['When']['HO_AnniversaryFamily'] == 'true')
        if 'addTemporaryActor' in body:
            assert 'If !PLAYER_HAS_MAIL Current HarveyFamily_PhotoTaken Received ## AddMail' in body
            assert 'AddMail Current HarveyFamily_PhotoTaken Received' in body.split('/')[4]
    marriage = read(ROOT / 'assets/Code/eventsMarriage.json')['Changes']
    first = [key for ch in marriage for key in ch.get('Entries', {}) if key.startswith('HarveyOverhaulMarriage.M3_')]
    assert len(first) == 1
    assert '!PLAYER_HAS_MAIL Current HarveyMarriage_AnniversarySecond Received' in first[0]
    assert '!PLAYER_HAS_MAIL Current HarveyMarriage_AnniversaryLater Received' in first[0]

    furniture = entries(changes, 'Data/Furniture')
    memories = entries(changes, 'Mods/{{ModId}}/Keepsakes')
    mail = entries(changes, 'Data/Mail')
    triggers = entries(changes, 'Data/TriggerActions')
    assert len(furniture) == len(memories) == len(mail) == len(triggers) == 5
    assert set(furniture) == set(memories)
    atlas = Image.open(ROOT / 'assets/Furniture/keepsakes.png').convert('RGBA')
    assert atlas.size == (160, 32)
    assert set(atlas.getchannel('A').get_flattened_data()) == {0, 255}
    attachment_ids = []
    all_bodies = '\n'.join(body for _, _, body in events)
    all_bodies += '\n'.join(v for ch in marriage for v in ch.get('Entries', {}).values())
    for item, value in furniture.items():
        fields = value.split('/')
        assert len(fields) == 11 and fields[1] in ('decor', 'painting') and fields[10] == 'true'
        assert fields[9].replace('\\', '/') == 'Mods/{{ModId}}/KeepsakeSprites'
        width, height = [int(n) * 16 for n in fields[2].split()]
        index = int(fields[8])
        x, y = index % 10 * 16, index // 10 * 16
        assert x + width <= atlas.width and y + height <= atlas.height
        assert atlas.crop((x, y, x + width, y + height)).getbbox(), item
        assert memories[item]['Description'] and memories[item]['HarveyLine']
        for choice in memories[item].get('Choices', []):
            assert f'AddMail Current {choice["Flag"]} Received' in all_bodies
            assert choice['Description'] != memories[item]['Description']
    for mail_id, text in mail.items():
        attached = re.findall(r'%item id \(F\)(\S+) 1%%', text)
        assert len(attached) == 1 and attached[0] in furniture
        attachment_ids += attached
        reward = [t for t in triggers.values() if t['Actions'] == [f'AddMail Current {mail_id} now']]
        assert len(reward) == 1 and reward[0]['Trigger'] == 'DayStarted'
        assert f'!PLAYER_HAS_MAIL Current {mail_id} Any' in reward[0]['Condition']
    assert set(attachment_ids) == set(furniture)
    journal = entries(read(ROOT / 'assets/Code/storyJournal.json')['Changes'],
                      'Mods/marilynsinister.HarveyOverhaul/StoryJournal')
    journal_ids = {eid for entry in journal.values() for eid in entry['EventIds'].split()}
    assert all(key.split('/')[0] in journal_ids for _, key, _ in events)
    print('Family life: all static checks passed.')


if __name__ == '__main__':
    main()
