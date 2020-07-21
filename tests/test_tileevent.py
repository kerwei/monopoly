import unittest2

import tile


class TestTileEvent:
    def testEventHasAllCards(self):
        """
        16 Chance cards in total
        """
        self.assertEqual(len(self.tile.deck), 16)


class TestTileChance(TestTileEvent, unittest2.TestCase):
    def setUp(self):
        self.tile = tile.TileChance()


class TestTileCommunityChest(TestTileEvent, unittest2.TestCase):
    def setUp(self):
        self.tile = tile.TileCommunityChest()