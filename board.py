import random

from collections import Counter
from collections.abc import Callable
from itertools import chain, cycle, product
from typing import List, Sequence

import player
import tile
from player import Player
from tile import Tile, TileFactory

class ItemCycler:
    def __init__(self, lst_items: list):
        self.roll = cycle(lst_items)

    def issue_next(self) -> Player:
        return next(self.roll)


class Dice:
    def __init__(self, dice_type: str='hexa', n: int=2):
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

        self.distribution = self.generate_distribution()

    def roll(self):
        """
        Returns the outcome of one roll
        """
        return random.choices(self.face, k=self.dice_count)

    def generate_distribution(self) -> dict:
        """
        Returns the distribution of outcome of the rolls
        doubles: same int on both dice
        singles: different int on both dice
        regular: all possible rolls from a 2x 6-sided dice
        Currently hard-coded to a double reroll, third strike format.

        TODO: Allow other dice roll formats
        All possible outcome:
            1. singles
            2. doubles -> singles
            3. doubles -> doubles -> regular
        """
        n_outcome = max(self.face) ** self.dice_count

        # Regular
        regular = [i for i in product(self.face, self.face)]
        regular_sum = [sum(i) for i in regular]

        # Singles
        single_sum = [sum(i) for i in regular if i[0] != i[1]]
        p_single = {k: v/(n_outcome) for k, v in Counter(single_sum).items()}

        # Doubles
        double_sum = [sum(i) for i in regular if i[0] == i[1]]
        _p_double = 1/n_outcome

        # Doubles -> Singles
        dblsgl_sum = [sum(i) for i in product(double_sum, single_sum)]
        p_dblsgl = {
            k: v * (_p_double ** 2) for k, v in Counter(dblsgl_sum).items()}

        # Doubles -> Doubles -> Singles
        dbldblsgl_sum = [sum(i) for i in product(
            double_sum, double_sum, regular_sum)]
        p_dbldblsgl = {
            k: v * (_p_double ** 3) for k, v in Counter(dbldblsgl_sum).items()}

        p_outcome = {}
        for i in range(3, n_outcome + 1):
            p_outcome[i] = \
                p_single.get(i, 0) + \
                p_dblsgl.get(i, 0) + \
                p_dbldblsgl.get(i, 0)

        return p_outcome


class Board:
    """
    The main board game class
    """
    def __init__(self, lst_player: Sequence[List[str]], schema: dict):
        # For now players are added based on list sequence. A method will be
        # added to determine the turn of each player later
        self.players = {p: Player(p) for p in lst_player}
        lst_turn = self.assign_turns_by_shuffling()
        self.player_roll = ItemCycler([self.players[p] for p in lst_turn])

        self.colorgrp = {}
        for dct in schema['board-sg'].values():
            if dct.get('color'):
                self.colorgrp[dct['color']] = {}

        self.lst_tile = []
        self.player_location = {p.token: 0 for p in self.players.values()}
        self.player_nround = {p.token: 1 for p in self.players.values()}

        # Community Chest and Chance decks should be initialized only once
        # since cards are drawn from the same instance
        self._community_chest = tile.TileCommunityChest()
        self._chance = tile.TileChance()

        # Build the board
        self.build_board(schema)
        self.dice = Dice(dice_type='hexa', n=2)

    @property
    def leader(self) -> list:
        """
        Tracks the player that has made the most number of moves across
        the tiles
        """
        leader = []
        maxsteps = float('-inf')

        for p in self.players:
            steps = self.player_location[p] + \
                self.player_nround[p] * 40

            p = self.players[p]     # Convert token to the Player object
            if steps == maxsteps:
                leader.append(p)
            elif steps > maxsteps:
                leader = [p]
                maxsteps = steps

        return leader

    @property
    def last(self) -> list:
        """
        Tracks the player that has made the most number of moves across
        the tiles
        """
        last = []
        minsteps = float('inf')

        for p in self.players:
            steps = self.player_location[p] + \
                self.player_nround[p] * 40

            p = self.players[p]     # Convert token to the Player object
            if steps == minsteps:
                last.append(p)
            elif steps < minsteps:
                last = [p]
                minsteps = steps

        return last

    def assign_turns_by_shuffling(self) -> list:
        """
        Assign the turn for each player
        """
        lst_token = self.players.keys()
        return random.sample(lst_token, len(lst_token))

    def build_board(self, schema: dict) -> None:
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

    def calculate_terrain_value(self, player: Player) -> float:
        """
        Return the series of realizable tile values for this player
        """
        p_loc = self.player_location[player.token]

        moves = [k for k in self.dice.distribution.keys()]
        move_range = max(moves) - min(moves)

        lst_terrain = self.lst_tile[p_loc + min(moves):]
        if len(lst_terrain) >= move_range:
            lst_terrain = lst_terrain[:move_range + 1]
        else:
            balance = move_range - len(lst_terrain)
            lst_terrain += self.lst_tile[:balance]

        pval = self.dice.distribution
        terrain_value = [0] * len(lst_terrain)
        # Count of tiles in a group belonging to the owner
        for i, tile in enumerate(lst_terrain, start=min(moves)):
            if not getattr(tile, 'color', None):
                terrain_value[i - min(moves)] = tile.get_charges() * pval[i]
                continue

            ntile = self.colorgrp[tile.color].get(tile.owner, 0)
            terrain_value[i - min(moves)] = \
                tile.value_to(player.token, ntile) * pval[i]

        return sum(terrain_value)

    def liquidate_player(self, player: Player, f: Callable[..., str]) -> bool:
        """
        Liquidate the assets of a player until the balance becomes positive.
        Takes the liquidation strategy function as the second argument, which
        makes the decision on which asset to liquidate next.
        Returns True if player's balance returns to positive, else False
        """
        while player.balance < 0:
            tile = f(player)
            self.player_sell(tile, player)

            if not player.assets:
                return False

        return True

    def move_to_index(self, player: Player, n: int, pastgo: bool=True):
        """
        Move the player token by the index number. Add 1 to round count if
        moving past the GO tile
        """
        if pastgo and self.player_location[player.token] > n:
            self.player_nround[player.token] += 1

        self.player_location[player.token] = n

    def move_by_steps(self, player: Player, n: int):
        """
        Move the player token by the number of steps. Add 1 to round count if
        moving past the GO tile
        """
        if (self.player_location[player.token] + n) // 40 > 0:
            self.player_nround[player.token] += 1

        self.player_location[player.token] = \
            (self.player_location[player.token] + n) % 40

    def play_next_turn(self) -> None:
        """
        Play out the turn of the next player in queue
        """
        this_player = self.player_roll.issue_next()
        # Roll the dice and move
        self.roll_till_move(this_player)
        # Generate all available actions
        this_player_tile = self.player_location[this_player]
        lst_actions = this_player_tile.get_action(this_player)
        # Evaluate the available actions
        print(lst_actions)

    def player_buy(self, tile: Tile, player: Player) -> None:
        """
        Execute a buy transaction for the player
        """
        # Reduce player cash by tile cost
        player.pay(tile.cost['title'])
        # Set player as the owner of the tile
        tile.owner = player.token
        # Update property group dict
        self.colorgrp[tile.color][player.token] = \
            self.colorgrp[tile.color].get(player.token, 0) + 1

    def player_sell(self, tile: Tile, player: Player) -> None:
        """
        Execute a sell transaction for the player
        """
        # Reduce player cash by tile cost
        player.receive(tile.cost['title'])
        # Set player as the owner of the tile
        tile.owner = None
        # Update property group dict
        self.colorgrp[tile.color][player.token] -= 1

    def roll_till_move(self, player: Player) -> None:
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

    def transact(self, payer: Player, receipt: Player, amount: int) -> int:
        """
        Execute a pay and receive transaction
        Returns 1 if complete and 0 if the payer has insufficient balance
        """
        receipt.receive(amount)
        payer.pay(amount)

        if payer.balance < 0:
            self.liquidate_player(payer)

        return