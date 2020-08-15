import json
import os
import unittest2

import board
import player
import tile

from common import ROOTDIR, DATADIR


class TestCreateBoard(unittest2.TestCase):
    def setUp(self) -> None:
        # Load the monopoly-sg schema
        with open(
            os.path.join(DATADIR, 'schema_monopoly_sg.json'), 'r'
        ) as f:
            self.schema = json.load(f)
        self.lst_token = ['apple','boot','car','dog']
        self.players = [player.Player(p) for p in self.lst_token]

        # # Use double six-sided dice
        self.dice = board.Dice(dice_type='hexa', n=2)

    def tearDown(self) -> None:
        pass

    def testCreateBoard(self):
        """
        Make sure that the board can be created
        """
        self.new_board = board.Board(self.lst_token, schema=self.schema)
        self.assertIsInstance(self.new_board, board.Board)

    def testHasAllPlayers(self):
        """
        Make sure that all players are included
        """
        self.new_board = board.Board(self.lst_token, schema=self.schema)

        all_players = [p.token for p in self.players]
        board_players = [p.token for p in self.new_board.players]

        self.assertItemsEqual(all_players, board_players)

    def testHasAllTiles(self):
        """
        Make sure that the schema is loaded properly
        """
        self.new_board = board.Board(self.lst_token, schema=self.schema)

        tile_names = [k['name'] for k in self.schema['board-sg'].values()]
        board_tiles = [t.name for t in self.new_board.lst_tile]

        self.assertItemsEqual(tile_names, board_tiles)

    def testDiceRoll(self):
        """
        Dice rolls should behave as expected
        Make 100 rolls and check that the range falls between 2 and 12
        """
        scorecard = {}
        for i in range(1000):
            scorecard[sum(self.dice.roll())] = 1

        # A double six-sided die roll cannot be greater than 12
        self.assertEqual(max(scorecard.keys()), 12)

        # A double six-sided die roll cannot be less than 2
        self.assertEqual(min(scorecard.keys()), 2)

    def testMoveToIndex(self):
        """
        It is possible to change the location of a player
        by specifying the index or the number of steps
        """
        self.new_board = board.Board(self.lst_token, schema=self.schema)

        # Get the identity of the first player
        first = self.new_board.player_roll.issue_next()

        # At the start, all players are located on the GO tile
        self.assertEqual(
            self.new_board.player_location[first.token],
            0
        )

        # Move the player to Jail
        self.new_board.move_to_index(first, 10)
        self.assertEqual(
            self.new_board.player_location[first.token],
            10
        )

    def testMoveBySteps(self):
        """
        It is possible to change the location of a player
        by specifying the index or the number of steps
        """
        self.new_board = board.Board(self.lst_token, schema=self.schema)

        # Get the identity of the first player
        first = self.new_board.player_roll.issue_next()

        # At the start, all players are located on the GO tile
        self.assertEqual(
            self.new_board.player_location[first.token],
            0
        )

        # Move the player to Jail
        self.new_board.move_by_steps(first, 6)
        self.assertEqual(
            self.new_board.player_location[first.token],
            6
        )

    def testRaceOneLap(self):
        """
        Players race each other to make one full round across the board back
        to the GO tile
        """
        self.new_board = board.Board(self.lst_token, schema=self.schema)

        # Players take turns to move until one of them races past the GO tile
        # for the first time
        while set(self.new_board.player_nround.values()) == {1}:
            active_player = self.new_board.player_roll.issue_next()
            self.new_board.roll_till_move(active_player)

        """
        A minimum of 2 rounds will be required to race past the GO tile from
        the starting spot. Therefore, trailing player locations will have a 
        lower bound of 6 (rolling a 2 results in a bonus roll and thus, the 
        lowest number of steps a player can make is 3). The location index of
        the leader should not be greater than 39
        """
        # Check that the leader's location index is not greater than 39
        leader = self.new_board.leader
        self.assertLessEqual(
            self.new_board.player_location[leader.token],
            39
        )

        # Check that the last player in the race is not standing at location
        # index of less than 6
        last = self.new_board.last
        self.assertGreaterEqual(
            self.new_board.player_location[last.token],
            6
        )

        # Check that the location index of all players fall between 0 - 39
        self.assertTrue([
            0 <= x <= 39 for x in self.new_board.player_location.keys()])
