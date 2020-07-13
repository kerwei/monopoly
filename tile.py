import abc


class Tile(metaclass=abc.ABCMeta):
    def __init__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_actions(self, token: str):
        raise NotImplementedError


class TilePurchasable(Tile):
    """
    Metaclass for properties, infra and utils
    """
    @abc.abstractmethod
    def liquidate(self):
        raise NotImplementedError

    @abc.abstractmethod
    def acquire(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_charges(self):
        raise NotImplementedError


class TileProperty(TilePurchasable):
    capacity = {
        'house': 4,
        'hotel': 1
    }

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
    
    def liquidate(self) -> int:
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

    def get_charges(self, n_tile: int) -> int:
        """
        Calculate the charges upon this visitor. n_tile is the number of same-
        color tiles owned by the owner of this tile (to be supplied by the
        Board class)
        """
        # Charges on the title
        tile_fee = self.schedule_fee['title'] * n_tile

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

        self.construct_count[contype] += 1

        return self.cost[contype]


class TileInfra(TilePurchasable):
    def __init__(self, schema: dict):
        self.name = schema['name']
        self.idx = schema['idx']
        self.color = schema['color']
        self.cost = schema['cost']
        self.schedule_fee = schema['schedule']
        self.owner = None
    
    def liquidate(self) -> int:
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

    def get_charges(self, n_tile: int) -> int:
        """
        Calculate the charges upon this visitor. n_tile is the number of same-
        color tiles owned by the owner of this tile (to be supplied by the
        Board class)
        """
        return self.schedule_fee['title'] * n_tile


class TileEvent(Tile):
    """
    Chance, Community Chest, Taxes, Go To Jail, GO
    """
    def __init__(self, schema: dict):
        self.name = schema['name']

    def get_actions(self, token: str):
        raise NotImplementedError


class TileStatic(Tile):
    """
    Free Parking, Jail - Just Visiting
    """
    def __init__(self, schema: dict):
        self.name = schema['name']

    def get_actions(self, token: str) -> None:
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
            return TileEvent(schema)
        elif tiletype == 'static':
            return TileStatic(schema)
