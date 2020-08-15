import player
import random
import tile

from itertools import cycle
from tile import TileFactory


class ItemCycler:
    def __init__(self, lst_items: list):
        self.roll = cycle(lst_items)

    def issue_next(self) -> "list_element":
        return next(self.roll)


class Dice:
    def __init__(self, dice_type: str='hexa', n: int=2) -> tuple:
        """
        Default to 2 dice
        """
        self.dice_count = n

        if dice_type == 'quad':
            self.face = range(1,5)
        elif dice_type == 'hexa':
            self.face = range(1,7)
        elif dice_type == 'octa':
            self.face = range(1,9)

    def roll(self):
        """
        Returns the outcome of one roll
        """
        return random.choices(self.face, k=self.dice_count)


class Board:
    """
    The main board game class
    """
    def __init__(self, lst_player: list, schema: dict):
        # For now players are added based on list sequence. A method will be
        # added to determine the turn of each player later
        self.players = [player.Player(p) for p in lst_player]
        self.assign_turns_by_shuffling()
        self.player_roll = ItemCycler(self.players)

        self.lst_tile = []
        self.player_location = {p.token: 0 for p in self.players}

        # Community Chest and Chance decks should be initialized only once
        # since cards are drawn from the same instance
        self._community_chest = tile.TileCommunityChest()
        self._chance = tile.TileChance()

        # Build the board
        self.build(schema)
        self.dice = Dice(dice_type='hexa', n=2)

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

    def move_to_index(self, player: player.Player, n: int):
        self.player_location[player.token] = n

    def move_by_steps(self, player: player.Player, n: int):
        self.player_location[player.token] = \
            (self.player_location[player.token] + n) % 40

    def play_next_turn(self) -> None:
        """
        Play out the turn of the next player in queue
        """
        this_player = self.player_roll.issue_next()

    def roll_till_move(self, player: player.Player):
        """
        Determine how the dice roll is interpreted i.e. if it's a pair, then
        the player gets a reroll and if 3 pairs get rolled in a row, go to jail
        """
        roll_one, roll_two = self.dice.roll()
        i = 1
        steps = sum([roll_one, roll_two])

        while all([roll_one == roll_two, i < 3]):
            roll_one, roll_two = self.dice.roll()
            steps += sum([roll_one, roll_two])
            i += 1

        if i == 3:
            player.jail = True
            self.move_to_index(player, 10)
            return

        self.move_by_steps(player, steps)