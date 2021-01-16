from agent.default_agent import NaiveAgent
from agent.metaclass import Agent

def create_player_agent(agent: str, token: str) -> "Agent":
    if agent == 'default':
        agent = NaiveAgent

    return Agent(agent=agent, token=token)