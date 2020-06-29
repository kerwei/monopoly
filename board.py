import player


class Board:
    """
    The main board game class
    """
    def __init__(self, lst_player: list, schema: dict):
        # For now players are added based on list sequence. A method will be
        # added to determine the turn of each player later
        self.roster = {
            i: player.Player() for i, name in lst_player
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


class Tile:
    """
    Each tile on the board
    """
    capacity = {
        'house': 4,
        'hotel': 1
    }

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.color = kwargs['color']
        self.cost = kwargs['cost']
        self.schedule_fee = kwargs['schedule']

        self.construct_count = {
            'house': 0,
            'hotel': 0
        }
        self._owner = None
    
    def liquidate(self):
        """
        Sell this tile. Returns the proceeds from the sale
        """
        self.owner = None
        return self.cost['title']

    def acquire(self, name: str):
        """
        Purchase this tile. Returns the cost of the title
        """
        self.owner = name
        return self.cost['title']

    def get_charges(self, n_tile: int):
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

    def add_construct(self, contype: str, qty: int=1):
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
