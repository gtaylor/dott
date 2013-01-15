import unittest
from src.daemons.server.parent_loader.loader import ParentLoader

class ParentLoaderTests(unittest.TestCase):
    def setUp(self):
        self.loader = ParentLoader()

    def tearDown(self):
        del self.loader

    def test_simple_load(self):
        parent = self.loader.load_parent('src.game.parents.base_objects.room.RoomObject')
        self.assertEqual(parent.__name__, 'RoomObject')