"""Regression fixtures for failures the old coordinate checker silently missed."""
import unittest
from unittest.mock import patch

from event_staging import stage_script
from validate_event_staging import Audit


class Lane:
    def problem(self, x, y):
        return 'стена/предмет (Buildings)' if (x, y) == (1, 0) else None


class EventStagingChecks(unittest.TestCase):
    def audit(self, body, forks=()):
        entries = [('fixture.json', 'Lane', 'Main/Time 600 2600',
                    'none/2 2/farmer 1 1 1 Harvey 3 1 3/' + body), *forks]
        with patch('validate_event_staging.variants', return_value=[('', Lane(), {})]):
            return {row[3] for row in Audit(entries).run()}

    def test_answer_branches_are_walked(self):
        self.assertIn('TILE', self.audit('quickQuestion #Yes#No(break)move farmer 0 -1 0(break)emote farmer 40/end'))

    def test_forks_inherit_the_actor_positions(self):
        fork = ('fixture.json', 'Lane', 'Other', 'move farmer 0 -1 0/end')
        self.assertIn('TILE', self.audit('fork Other/end', [fork]))

    def test_advanced_moves_check_intermediate_tiles(self):
        self.assertIn('TILE', self.audit('advancedMove farmer false 0 -2/end'))

    def test_missing_headers_fail(self):
        entries = [('fixture.json', 'Lane', 'Main', 'continue/skippable/pause 200/end')]
        with patch('validate_event_staging.variants', return_value=[('', Lane(), {})]):
            self.assertIn('HEADER', {row[3] for row in Audit(entries).run()})

    def test_wrong_show_frame_argument_order_fails(self):
        self.assertIn('SYNTAX', self.audit('showFrame farmer true 117/end'))

    def test_looping_pose_must_stop_before_walking(self):
        self.assertIn('POSE', self.audit('animate farmer false true 500 4 5/move farmer 1 0 1/end'))

    def test_consecutive_asynchronous_moves_need_a_barrier(self):
        self.assertIn('RACE', self.audit('move farmer 1 0 1 true/move farmer 0 1 2/end'))

    def test_pixel_offsets_must_reset_before_walking(self):
        self.assertIn('OFFSET', self.audit('positionOffset farmer 32 0/move farmer 1 0 1/end'))

    def test_missing_npc_is_reported(self):
        self.assertIn('ACTOR', self.audit('speak Maru "Hello"/end'))

    def test_actors_cannot_share_the_same_position(self):
        self.assertIn('OVERLAP', self.audit('warp Harvey 1 1/speak Harvey "Hello"/end'))

    def test_multiple_actors_in_move_are_checked(self):
        self.assertIn('TILE', self.audit('move Harvey 1 0 1 farmer 0 -1 0/end'))

    def test_fixed_motion_is_idempotent(self):
        original = 'none/2 2/farmer 1 1 1 Harvey 3 1 3/animate farmer false true 100 4 5/move farmer 1 0 1 true/move farmer 0 1 2/end'
        fixed = stage_script(original)
        self.assertIn('stopAnimation farmer/move farmer', fixed)
        self.assertIn('proceedPosition farmer/move farmer', fixed)
        self.assertEqual(stage_script(fixed), fixed)

    def test_farm_tokens_disable_automatic_offset(self):
        fixed = stage_script('none/{{HO_FarmX}} {{HO_FarmY0}}/farmer {{HO_FarmX}} {{HO_FarmY1}} 2/end')
        self.assertEqual(fixed.split('/')[3], 'ignoreEventTileOffset')

    def test_quote_aware_split(self):
        self.assertEqual(stage_script('none/2 2/farmer 1 1 1/speak farmer "A/B"/end'),
                         'none/2 2/farmer 1 1 1/speak farmer "A/B"/end')

    def test_non_looping_animation_needs_time_before_replacement(self):
        self.assertIn('TIMING', self.audit('animate Harvey false false 350 22 20 22/stopAnimation Harvey/end'))
        self.assertIn('TIMING', self.audit('animate Harvey false false 350 22 20 22/pause 700/stopAnimation Harvey/end'))
        self.assertNotIn('TIMING', self.audit('animate Harvey false false 350 22 20 22/pause 1050/stopAnimation Harvey/end'))

    def test_npc_show_frame_does_not_cancel_a_loop(self):
        self.assertIn('POSE', self.audit('animate Harvey false true 100 22 20/showFrame Harvey 12/end'))

    def test_exit_checks_inherited_player_pose(self):
        fork = ('fixture.json', 'Lane', 'Other', 'end')
        self.assertIn('POSE', self.audit('showFrame farmer 107/fork Other/stopAnimation farmer/end', [fork]))

    def test_exit_waits_for_asynchronous_walk(self):
        self.assertIn('RACE', self.audit('move Harvey 1 0 1 true/end'))

    def test_stop_animation_end_frame_is_validated(self):
        with patch.object(Audit, 'check_frame') as check:
            self.audit('stopAnimation Harvey 999/end')
            check.assert_called_with('Harvey', 999, 'stopAnimation Harvey 999')

    def test_absolute_farm_tokens_require_offset_opt_out(self):
        entries = [('fixture.json', 'Farm', 'Main',
                    'none/2 2/farmer {{HO_FarmX}} 1 1/end')]
        with patch('validate_event_staging.variants', return_value=[('', Lane(), {'HO_FarmX': '2'})]):
            self.assertIn('OFFSET', {row[3] for row in Audit(entries).run()})

    def test_trigger_actions_need_the_event_action_wrapper(self):
        self.assertIn('COMMAND', self.audit('removeConversationTopic topicAgreedCheckup/end'))
        self.assertNotIn('COMMAND', self.audit('action RemoveConversationTopic topicAgreedCheckup/end'))


if __name__ == '__main__':
    unittest.main()
