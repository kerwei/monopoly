import agent
import player
import unittest

from agent import create_player_agent

class TestAgent(unittest.TestCase):
    def setUp(self):
        pass

    def test_agent_inheritance(self):
        ag = create_player_agent('one', 'test')
        self.assertTupleEqual(
            type(ag).__mro__, 
            (
                agent.TestAgentOne, 
                agent.Agent, 
                player.Player, 
                agent.BaseAgent, 
                agent.AbstractAgent, 
                object))