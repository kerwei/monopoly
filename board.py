import player
import random
import tile

from tile import TileFactory


class Board:
    """
    The main board game class
    """
    def __init__(self, lst_player: list, schema: dict):
        # For now players are added based on list sequence. A method will be
        # added to determine the turn of each player later
        self.players = [player.Player(p) for p in lst_player]
        self.assign_turns_by_shuffling()

        self.lst_tile = []
        self.community_chest = tile.TileCommunityChest()
        self.chance = tile.TileChance()

        # Build the board
        self.build(schema)

    def assign_turns_by_shuffling(self):
        """
        Assign the turn for each player
        """
        random.shuffle(self.players)

    def build(self, schema: dict) -> None:
        """
        Constructs the full board
        """
        for v in schema['board-sg'].values():
            if 'chance' in v['name'].lower():
                self.lst_tile += [self._chance]
            elif 'community' in v['name'].lower():
                self.lst_tile += [self._community_chest]
            else:
                self.lst_tile += [TileFactory.create(v)]