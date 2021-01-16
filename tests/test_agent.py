import json
import os
import unittest

import agent
import player

from agent.agent_factory import create_player_agent
from agent.default_agent import NaiveAgent
from agent.metaclass import Agent, BaseAgent, AbstractAgent

from common import ROOTDIR, DATADIR


class TestAgent(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(DATADIR, 'schema_monopoly_sg.json'), 'r') as f:
            self.schema = json.load(f)

    def test_agent_inheritance(self):
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