import player
import tile


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
        self.schema = schema

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