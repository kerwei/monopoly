import abc
import json
import os
import random
from typing import Optional

from common import DATADIR, capacity


class Tile(metaclass=abc.ABCMeta):
    def __init__(self):
        self.owner = None

    @abc.abstractmethod
    def get_action(self, token: str) -> list:
        """
        All available actions to this player
        """
        raise NotImplementedError

    def value_to(self, token: str, ntile: int) -> float:
        """
        The cost incurred from landing on this tile to this player
        """
        if not self.owner or token == self.owner:
            return 0

        return self.get_charges(str(ntile))

    def get_charges(self, ntile: Optional[str]='0') -> int:
        """
        Standard method for the Tile class. Returns 0
        """
        return 0

class TilePurchasable(Tile):
    """
    Metaclass for properties, infra and utils
    """
    @abc.abstractmethod
    def liquidate_title(self):
        raise NotImplementedError

    @abc.abstractmethod
    def acquire(self):
        raise NotImplementedError

    def get_action(self, visitor: str) -> list:
        """
        Return a list of valid actions for the visitor
        """
        if self.owner and visitor != self.owner:
            return [tuple(['pay', {'payer': visitor, 'payee': self.owner}])]
        elif not self.owner:
            return [tuple(['acquire', {'tile': self.name}])]

        return None


class TileProperty(TilePurchasable):
    def __init__(self, schema: dict):
        self.name = schema['name']
        self.idx = schema['idx']
        self.color = schema['color']
        self.cost = schema['cost']
        self.schedule_fee = schema['schedule']

        self.construct_count = {
            'house': 0,
            'hotel': 0
        }

        self.owner = None

    def get_action(self, visitor: str) -> list:
        """
        Return a list of valid actions for the visitor
        """
        actions = super().get_action(visitor)

        if actions[0] == 'liquidate_title':
            # Maximum of 1 hotel and 4 houses
            if self.construct_count['house'] < 4:
                for i in range(1, self.construct_count['house'] + 1):
                    actions += [
                        tuple(['sell_construct', {'type': 'house', 'amt': i}])]

                for i in range(1, 5 - self.construct_count['house']):
                    actions += [
                        tuple(['add_construct', {'type': 'house', 'amt': i}])]

            if self.construct_count['house'] == 4 and \
                not self.construct_count['hotel']:
                actions += [
                    tuple(['add_construct', {'type': 'hotel', 'amt': 1}])]
            elif self.construct_count['hotel']:
                actions += [
                    tuple(['sell_construct', {'type': 'hotel', 'amt': 1}])]

        return actions

    def liquidate_constructs(self) -> int:
        """
        Sell the constructed buildings. Returns the proceeds from the sale
        """
        constructs = sum([v for k, v in self.construct_count.items()])
        if not constructs:
            raise Exception('No more constructs on this tile')

        # Constructs can only be sold in sequence: hotels -> house
        if self.construct_count['hotel']:
            self.construct_count['hotel'] -= 1
            return self.cost['hotel']

        self.construct_count['house'] -= 1
        return self.cost['house']

    def liquidate_title(self) -> int:
        """
        Sell this tile. Returns the proceeds from the sale
        TODO: This should also recursively sell all constructs
        """
        construct = sum([v for k, v in self.construct_count.items()])
        if construct:
            raise Exception('Tile is not empty of constructs')

        self.owner = None
        return self.cost['title']

    def acquire(self, name: str) -> int:
        """
        Purchase this tile. Returns the cost of the title
        """
        self.owner = name
        return self.cost['title']

    def get_charges(self, ntile: str) -> int:
        """
        Calculate the charges upon this visitor. n_tile is the number of same-
        color tiles owned by the owner of this tile (to be supplied by the
        Board class)
        """
        # Charges on the title
        tile_fee = self.schedule_fee['title'].get(ntile, 0)
        # Charges on the constructed properties
        construct_fee = \
            self.construct_count['house'] * self.schedule_fee['house'] \
            + self.construct_count['hotel'] * self.schedule_fee['hotel']

        return tile_fee + construct_fee

    def add_construct(self, contype: str, qty: int=1) -> int:
        """
        Add house or hotel units to this tile. Returns the cost of construction
        or 0 if the capacity is full
        Rules:
            1. House capacity: 4 Hotel capacity: 1
            2. House capacity needs to be maxed first before a hotel can be
               built
        
        """
        if self.construct_count[contype] == capacity[contype]:
            return 0

        self.construct_count[contype] += qty

        return self.cost[contype]


class TileInfra(TilePurchasable):
    def __init__(self, schema: dict):
        self.name = schema['name']
        self.idx = schema['idx']
        self.color = schema['color']
        self.cost = schema['cost']
        self.schedule_fee = schema['schedule']
        self.owner = None
    
    def liquidate_title(self) -> int:
        """
        Sell this tile. Returns the proceeds from the sale
        """
        self.owner = None
        return self.cost['title']

    def acquire(self, name: str) -> int:
        """
        Purchase this tile. Returns the cost of the title
        """
        self.owner = name
        return self.cost['title']

    def get_charges(self, n_tile: str) -> int:
        """
        Calculate the charges upon this visitor. n_tile is the number of same-
        color tiles owned by the owner of this tile (to be supplied by the
        Board class)
        """
        return self.schedule_fee['title'].get(n_tile, 0)


class TileEvent(Tile):
    def __init__(self, schema: dict):
        self.name = schema['name']
        self.idx = schema['idx']

class TileIncomeTax(TileEvent):
    def __init__(self, schema: dict):
        super().__init__(schema)
        self.action = schema['pay']

    def get_action(self) -> list:
        """
        Pay to bank the specified amount
        """
        return [tuple([{'pay': self.action}])]

    def get_charges(self):
        """
        Set this to a fixed 2000 for now. Used for agent decision making
        """
        return 2000


class TileSuperTax(TileEvent):
    def __init__(self, schema: dict):
        super().__init__(schema)
        self.action = schema['pay']

    def get_action(self) -> list:
        """
        Pay to bank the specified amount
        """
        return [tuple([{'pay': self.action}])]

    def get_charges(self):
        """
        Set this to a fixed 750 for now. Used for agent decision making
        """
        return 750

class TileGO(TileEvent):
    def __init__(self, schema: dict):
        super().__init__(schema)
        self.action = schema['receive']

    def get_action(self) -> list:
        """
        Pay to bank the specified amount
        """
        return [tuple([{'pay': -self.action}])]


class TileGoToJail(TileEvent):
    def __init__(self, schema: dict):
        super().__init__(schema)
        self.action = schema['move']

    def get_action(self) -> list:
        """
        Pay to bank the specified amount
        """
        return [tuple([{'move': self.action}])]


class TileEventDeck(TileEvent):
    """
    Chance, Community Chest, Taxes, Go To Jail, GO
    """
    def __init__(self):
        self._load_schema()

        # Load the cards into a deck
        self.deck = [card_idx for card_idx in self.schema]
        self._shuffle_deck()

    def _load_schema(self) -> None:
        """
        Load schema from json file
        """
        with open(self.fpath, 'r') as f:
            self.schema = json.load(f)

    def _shuffle_deck(self) -> None:
        """
        Shuffle the order of the cards in the deck
        """
        random.shuffle(self.deck)

    def get_action(self) -> list:
        """
        Draw a card from the deck for the given player
        """
        drawn = self.deck.pop(0)
        # Move to the bottom of the deck
        self.deck.append(drawn)

        return [tuple([{'draw': self.schema[drawn]}])]


class TileChance(TileEventDeck):
    def __init__(self):
        self.name = 'Chance'
        self.fpath = os.path.join(DATADIR, 'schema_chance.json')
        super().__init__()


class TileCommunityChest(TileEventDeck):
    def __init__(self):
        self.name = 'Community Chest'
        self.fpath = os.path.join(DATADIR, 'schema_chest.json')
        super().__init__()


class EventFactory:
    @staticmethod
    def create(schema: dict) -> TileEvent:
        if schema['name'] == 'Income Tax':
            return TileIncomeTax(schema)
        elif schema['name'] == 'Go To Jail':
            return TileGoToJail(schema)
        elif schema['name'] == 'Super Tax':
            return TileSuperTax(schema)
        elif schema['name'] == 'GO':
            return TileGO(schema)

    def get_action(self, token: str) -> list:
        raise NotImplementedError


class TileStatic(Tile):
    """
    Free Parking, Jail - Just Visiting
    """
    def __init__(self, schema: dict):
        self.name = schema['name']

    def get_action(self, token: str) -> None:
        return None


class TileFactory:
    """
    Tile factory class
    """
    def create(schema: dict) -> Tile:
        tiletype = schema['type']

        if tiletype == 'property':
            return TileProperty(schema)
        elif tiletype == 'infra':
            return TileInfra(schema)
        elif tiletype == 'event':
            return EventFactory.create(schema)
        elif tiletype == 'static':
            return TileStatic(schema)
