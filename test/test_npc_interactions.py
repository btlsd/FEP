import unittest
from unittest.mock import patch

from characters import Player, NPCS
from game import Game


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


if __name__ == '__main__':
    unittest.main()
