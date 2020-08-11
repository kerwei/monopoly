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