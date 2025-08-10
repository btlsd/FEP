import unittest
from unittest.mock import patch

from characters import Player, NPCS
from game import Game
import io
from contextlib import redirect_stdout


class TestNPCInteraction(unittest.TestCase):
    def test_talk_to_trader(self):
        player = Player("Tester")
        trader = next(n for n in NPCS if n.name == "상인 정")
        player.location = trader.location
        game = Game(player)
        with patch('builtins.input', side_effect=['1', '1', '4']):
            game.interact()
        self.assertTrue(trader.is_alive())

    def test_hostile_robot_attacks(self):
        player = Player("Tester")
        robot = next(n for n in NPCS if n.name == "로봇 42")
        player.location = robot.location
        player.nation_affinity["전계국"] = 0
        game = Game(player)
        with patch('battle.start_battle', return_value=(True, 1)) as start_mock:
            with patch('builtins.input', side_effect=['1']):
                segs = game.interact()
        start_mock.assert_called_once()
        self.assertIsNotNone(segs)

    def test_no_immediate_repeat_greeting(self):
        player = Player("Tester")
        npc = next(n for n in NPCS if n.name == "상인 정")
        player.location = npc.location
        with patch('dialogues.greeting', return_value='HELLO'), \
             patch('builtins.input', side_effect=['4']):
            buf = io.StringIO()
            with redirect_stdout(buf):
                npc.talk(player)
            first = buf.getvalue()

        with patch('dialogues.greeting', return_value='HELLO'), \
             patch('builtins.input', side_effect=['4']):
            buf = io.StringIO()
            with redirect_stdout(buf):
                npc.talk(player)
            second = buf.getvalue()

        self.assertIn('HELLO', first)
        self.assertNotIn('HELLO', second)

    def test_revisit_greeting_after_time(self):
        player = Player("Tester")
        npc = next(n for n in NPCS if n.name == "상인 정")
        player.location = npc.location
        with patch('dialogues.greeting', return_value='HELLO'), \
             patch('builtins.input', side_effect=['4']):
            with redirect_stdout(io.StringIO()):
                npc.talk(player)

        player.time += 1

        with patch('messages.get_message', return_value='REHI'), \
             patch('builtins.input', side_effect=['4']):
            buf = io.StringIO()
            with redirect_stdout(buf):
                npc.talk(player)
            out = buf.getvalue()

        self.assertIn('REHI', out)


if __name__ == '__main__':
    unittest.main()
