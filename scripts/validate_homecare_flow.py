"""Ensure home recovery has one owner and romantic notes don't require soliciting mail."""
from pathlib import Path
import validate_event_coords as c

root = Path(c.CP_ROOT)
ids = {'eventHarveyAfterHospitalDischargeHome', 'eventHarveyAfterExternalRescueHome',
       'eventHarveyAfterExternalRescueHomeEngaged', 'eventHarveyAfterExternalRescueHomeMarried',
       'eventHarveyNightRoundSevereFirst', 'eventHarveyMorningAfterExhaustion'}
entries = [entry for entry in c.iter_event_entries() if entry[2].split('/')[0] in ids]
assert len(entries) == 6, [entry[2].split('/')[0] for entry in entries]
assert all('/GameStateQuery FALSE' in key for _, _, key, _ in entries), 'Injury must be the sole home-care launcher.'

doc = c.read_jsonc(root / 'assets/Code/courtshipLine.json')
triggers = {key: value for ch in doc['Changes'] if ch.get('Target') == 'Data/TriggerActions'
            for key, value in ch['Entries'].items()}
for suffix in ('Thanks', 'Miss', 'Dinner'):
    recipe = '{{ModId}}_Note' + suffix
    trigger = triggers['{{ModId}}_Courtship_LearnNote' + suffix]
    assert trigger['Trigger'] == 'DayStarted'
    assert 'PLAYER_NPC_RELATIONSHIP Current Harvey Dating Engaged Married' in trigger['Condition']
    assert '!PLAYER_HAS_CRAFTING_RECIPE Current ' + recipe in trigger['Condition']
    assert trigger['Actions'] == ['MarkCraftingRecipeKnown Current ' + recipe + ' true']
for change in doc['Changes']:
    for key, value in (change.get('Entries') or {}).items():
        if change.get('Target') == 'Data/Mail':
            continue  # Keep old recipe-mail IDs readable for already queued letters.
        assert 'AddMail Current {{ModId}}_mailNoteThanksRecipe' not in str(value)
        assert 'AddMail Current {{ModId}}_mailNoteMissRecipe' not in str(value)
        assert 'AddMail Current {{ModId}}_mailNoteDinnerRecipe' not in str(value)
print('Home care and note recipes: all checks passed.')
