import unittest
from src.server.db.objects.in_memory_store import InMemoryObjectStore

class InMemoryObjectStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryObjectStore(db_name='dott_objects_test')

    def tearDown(self):
        del self.store._server['dott_objects_test']

    def test_basic(self):
        """
        Makes sure the default DB is created with one room.
        """
        num_objects = len(self.store._objects)
        self.assertEqual(num_objects, 1)