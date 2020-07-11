import player
import tile

from tile import TileFactory


class Board:
    """
    The main board game class
    """
    def __init__(self, lst_player: list, schema: dict):
        # For now players are added based on list sequence. A method will be
        # added to determine the turn of each player later
        self.roster = {
            i: player.Player(token) for i, token in enumerate(lst_player)
        }

        self.lst_tile = []
        for k, v in schema['board-sg'].items():
            v['name'] = k
            self.lst_tile += [TileFactory.create(v)]

    def assign_turns(self):
        """
        Assign the turn for each player
        """
        raise NotImplementedError

    def build(self):
        """
        Constructs the full board
        """
        raise NotImplementedError