import unittest
from src.server.db.objects.in_memory_store import InMemoryObjectStore

class InMemoryObjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryObjectStore(db_name='dott_objects_test')

    def tearDown(self):
        del self.store._server['dott_objects_test']

    def test_starter_room_creation(self):
        """
        Makes sure the default DB is created with one room. Check some
        of the default values on it.
        """
        num_objects = len(self.store._objects)
        # There should only be one object at this point.
        self.assertEqual(num_objects, 1)

        # Get the starter room instance.
        id, room = self.store._objects.items()[0]
        # It should have been created with the standard room parent.
        self.assertEqual(room.parent, 'src.game.parents.base_objects.room.RoomObject')