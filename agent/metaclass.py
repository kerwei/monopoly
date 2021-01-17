import abc

from player import Player


class AbstractAgent(metaclass=abc.ABCMeta):
    """
    Abstract Agent class
    """
    @abc.abstractmethod
    def cp_asset_sale(self, amt: float) -> str:
        """
        Compute the next asset to sell based on defined strategy
        """
        raise NotImplementedError


class BaseAgent(AbstractAgent):
    pass


class Agent(Player, BaseAgent):
    def __new__(cls, **kwargs) -> "Agent":
        agent = kwargs['agent']
        return super(Agent, agent).__new__(agent)

    def __init__(self, **kwargs) -> None:
        super().__init__(kwargs['token'])