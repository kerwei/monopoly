from collections import defaultdict

from tile import Tile


class Player:
    """
    The player class
    """
    def __init__(self, token):
        self.token = token
        # Cash balance
        self.balance = 1500
        # List of properties owned
        self.assets = defaultdict(list)
        # List of favor cards owned
        self.favors = defaultdict(int)

    def pay(self, amount: int) -> None:
        """
        Reduce the balance of this player
        """
        self.balance -= amount

    def receive(self, amount: int) -> None:
        """
        Increase the balance of this player
        """
        self.balance += amount

    def asset_acquire(self, asset: Tile) -> None:
        """
        Add a property to the assets of this player
        """
        self.assets[asset.color] += [asset]

    def asset_liquidate(self, asset: Tile) -> None:
        """
        Remove a property from the assets of this player
        """
        self.assets[asset.color].pop(asset)