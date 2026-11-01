"""Check clinic scenes against Therapist NPC's installed partial Hospital edit.

Therapist 1.3 edits only (15,8)-(23,19), rather than replacing the whole map.
The upper ward and reception must still come from the underlying clinic map.
Run alongside check_all.py; no game or save is modified.
"""
from collections import deque
from pathlib import Path
from unittest.mock import patch

import validate_event_coords as c
import validate_event_staging as staging


class PatchedHospital:
    def __init__(self, base, therapist, area):
        self.base = base
        self.therapist = therapist
        self.area = area

    def problem(self, x, y):
        area = self.area
        if area['X'] <= x < area['X'] + area['Width'] and area['Y'] <= y < area['Y'] + area['Height']:
            return self.therapist.problem(x, y)
        return self.base.problem(x, y)


def reaches_reception(tmap, start):
    """A valid exit must connect to reception, not merely be an isolated floor tile."""
    queue = deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) == (10, 19):
            return True
        for tile in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if tile not in seen and tmap.problem(*tile) is None:
                seen.add(tile)
                queue.append(tile)
    return False


def main():
    root = Path(c.CP_ROOT)
    manifest = c.read_jsonc(root / 'manifest.json')
    assert any(d['UniqueID'] == 'Endwyr.TherapistNPC' and d.get('IsRequired') is False
               for d in manifest['Dependencies']), 'Load after Therapist when installed.'
    entries = list(c.iter_event_entries())
    recovery = [entry for entry in entries if entry[0] == 'collapse.json' and entry[2] == 'PlayerKilled']
    assert len(recovery) == 2, 'Check both Dating and Engaged recovery scenes.'
    for _, _, _, script in recovery:
        cmds = c.split_commands(script)
        assert cmds.count('hospitaldeath') == 1 and 'skippable' not in cmds, 'Apply death penalties exactly once.'
        assert cmds[-1] == 'end position 20 6', 'Do not return to the room now used by Grey.'
        assert cmds.index('positionOffset farmer 0 0') < cmds.index('warp farmer 20 6'), 'Clear the bed offset before standing.'

    base = c.load_map('Hospital')
    assert base is not None, 'Clinic map needed for spatial checks.'
    profiles = [('Alchemistry', base)]
    vanilla = c.load_path(str(Path(c.VANILLA) / 'Hospital.tmx'))
    if vanilla:
        profiles.append(('Vanilla (recovery)', vanilla))
    folder = Path(c.MODS) / '[Endwyr] TherapistNPC'
    if folder.exists():
        doc = c.read_jsonc(folder / 'Content.json')
        edit = next(ch for ch in doc['Changes'] if ch.get('Target') == 'Maps/Hospital' and ch['Action'] == 'EditMap')
        assert edit['FromArea'] == edit['ToArea'], 'Update QA for a relocated Therapist map patch.'
        therapist = c.load_path(str(folder / edit['FromFile']))
        assert therapist is not None
        profiles.append(('Alchemistry + Therapist NPC', PatchedHospital(base, therapist, edit['ToArea'])))
        if vanilla:
            profiles.append(('Vanilla + Therapist NPC (recovery)', PatchedHospital(vanilla, therapist, edit['ToArea'])))
        # Reproduce the screenshot: the old scene used passable bed coordinates
        # on Alchemistry which become office furniture in Therapist's edit.
        legacy = [('collapse.json', 'Hospital', 'PlayerKilled',
                   'none/-100 -100/farmer 20 12 2 Harvey 21 12 3/end')]
        with patch.object(staging, 'variants', return_value=[('Therapist regression', profiles[-1][1], {})]):
            assert any(row[3] == 'TILE' for row in staging.Audit(legacy).run()), 'QA must detect the original misplaced actors.'
    else:
        print('Therapist NPC is not installed; checking shared upper-ward recovery only.')

    original_variants = staging.variants
    for label, tmap in profiles:
        selected = recovery if '(recovery)' in label else [entry for entry in entries
                   if entry[1] == 'Hospital' or 'changeLocation Hospital' in entry[3]]

        def variants(location, fname, eid):
            return [(label, tmap, {})] if location == 'Hospital' else original_variants(location, fname, eid)

        with patch.object(staging, 'variants', side_effect=variants):
            audit = staging.Audit(entries)
            audit.entries = selected  # Keep fork definitions from other locations available.
            issues = audit.run()
        assert not issues, '\n'.join(map(str, issues))
        assert tmap.problem(19, 5) is None, f'{label}: Harvey must stand beside the bed.'
        assert tmap.problem(20, 5) is not None, f'{label}: expected a bed at the posed patient tile.'
        assert tmap.problem(20, 6) is None and reaches_reception(tmap, (20, 6)), f'{label}: recovery exit is blocked.'
        print(f'{label}: {len(selected)} event definitions checked; recovery exit reaches reception.')
    print('Therapist compatibility: all checks passed.')


if __name__ == '__main__':
    main()
