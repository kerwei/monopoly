import json
import os
import unittest2

import board
import player
import tile


ROOTDIR = os.path.dirname(os.path.dirname(__file__))
DATADIR = os.path.join(ROOTDIR, 'data')


class TestCreateBoard(unittest2.TestCase):
    def setUp(self) -> None:
        # Load the monopoly-sg schema
        with open(
            os.path.join(DATADIR, 'schema_monopoly_sg.json'), 'r'
        ) as f:
            self.schema = json.load(f)

        self.players = ['apple','boot','car','dog']
        self.roster = {
            'apple': None,
            'boot': None,
            'car': None,
            'dog': None
        }
        for p in self.players:
            self.roster[p] = player.Player(p)

    def tearDown(self) -> None:
        pass

    def testCreateBoard(self):
        """
        Make sure that the board can be created
        """
        self.new_board = board.Board(self.players, schema=self.schema)
        self.assertIsInstance(self.new_board, board.Board)

    def testHasAllPlayers(self):
        """
        Make sure that all players are included
        """
        self.new_board = board.Board(self.players, schema=self.schema)

        all_players = [p.token for p in self.roster.values()]
        board_players = [p.token for p in self.new_board.roster.values()]

        self.assertItemsEqual(all_players, board_players)

    def testHasAllTiles(self):
        """
        Make sure that the schema is loaded properly
        """
        self.new_board = board.Board(self.players, schema=self.schema)

        tile_names = [k for k in self.schema['board-sg']]
        board_tiles = [t.name for t in self.new_board.lst_tile]

        self.assertItemsEqual(tile_names, board_tiles)