import json
import os
import unittest
from unittest.loader import getTestCaseNames

import agent
import board
import player

from agent.agent_factory import create_player_agent
from agent.default_agent import NaiveAgent
from agent.metaclass import Agent, BaseAgent, AbstractAgent
from tests.test_board import allocate_sequence_ownership

from common import ROOTDIR, DATADIR


class TestAgent(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(DATADIR, 'schema_monopoly_sg.json'), 'r') as f:
            self.schema = json.load(f)

        self.lst_token = ['apple','boot','car','dog']

        # Use double six-sided dice
        self.dice = board.Dice(dice_type='hexa', n=2)
        # Init the board
        self.new_board = board.Board(self.lst_token, schema=self.schema)
        self.new_board = allocate_sequence_ownership(self.new_board)

    def test_agent_inheritance(self):
        """
        Check the integrity of the Agent mro
        """
        ag = create_player_agent('default', 'apple')
        self.assertTupleEqual(
            type(ag).__mro__, 
            (
                NaiveAgent, 
                Agent, 
                player.Player, 
                BaseAgent, 
                AbstractAgent, 
                object))

    def test_naive_cp_asset_sale_one(self):
        """
        Naive agent liquidates assets by minimizing the number of assets sold
        and minimizing the difference between liquidation value and the
        required amount
        """
        board = self.new_board
        board = allocate_sequence_ownership(board)
        arr_sell = board.players['apple'].cp_asset_sale(2400)

        self.assertSetEqual(set(arr_sell), {24})

    def test_naive_cp_asset_sale_two(self):
        """
        Naive agent liquidates assets by minimizing the number of assets sold
        and minimizing the difference between liquidation value and the
        required amount
        """
        board = self.new_board
        arr_sell = board.players['apple'].cp_asset_sale(2500)

        self.assertSetEqual(set(arr_sell), {8, 28})

    def test_naive_cp_take_action_one(self):
        """
        Naive agent will always choose to buy tiles/ install constructs as long
        as it has sufficient balance
        """
        gameboard = self.new_board
        apple = gameboard.players['apple']
        gameboard.move_to_index(apple, 8)   # Owned by apple

        tileon = gameboard.lst_tile[gameboard.player_location['apple']]
        lst_actions = tileon.get_action('apple')

        constructs = {k: v for k,v in tileon.construct_count.items()}
        choice = apple.cp_take_action(lst_actions)
        action = gameboard.dct_actions[choice.action]

        action(tileon, apple, **choice.params)
        self.assertTrue(
            any([tileon.construct_count['house'] > constructs['house'],
                tileon.construct_count['hotel'] > constructs['hotel']]))