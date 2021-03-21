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
        lst = list(itertools.chain(*[x for x in self.assets.values()]))
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

                if diff >= 0 and diff < surplus:
                    surplus = diff
                    combi = tuple([x[0] for x in grp])

            i += 1

        return None if not combi else combi

    def cp_take_action(self, lst_action: List) -> int:
        """
        Default strategy: Buy anything while enough cash, else do nothing.
        Return the list index of the action
        NOTE: Actions requiring payments will not be evaluated by this method.
        Given the non-exclusion nature of payments, the player's balance will
        be deducted as it happens, or the call to compute liquidate_assets will
        be invoked.
        """
        for action in lst_action:
            if action.action == 'acquire':
                return action

            if action.action == 'add_construct':
                return action

        return lst_action[0]    # Do nothing