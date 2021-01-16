import itertools

from collections import namedtuple
from typing import List, Tuple

from agent.metaclass import Agent
from tile import Tile


class NaiveAgent(Agent):
    def cp_asset_sale(self, amt: float) -> Tuple:
        """
        Default strategy: sell the least number of assets to cover shortfall
        """
        lst = list(itertools.chain(*[x for x in self.assets]))
        lst = [(getattr(x, 'idx'), getattr(x, 'cost').get('title')) \
            for x in lst]

        # Iterate from 1 and sequentially increased until the proceeds from the
        # sale is greater than the amount
        i = 1
        surplus = float('inf')
        combi = None
        while i <= len(lst):
            cbn = itertools.combinations(lst, i)

            for grp in cbn:
                diff = sum([x[1] for x in grp]) - amt

                if diff > 0 and diff < surplus:
                    surplus = diff
                    combi = tuple([x[0] for x in grp])

            if combi:
                break

            i += 1

        return None if not combi else combi
