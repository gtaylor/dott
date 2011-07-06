import unittest
from src.server.db.objects.in_memory_store import InMemoryObjectStore

class InMemoryStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryObjectStore(db_name='dott_objects_test')

    def tearDown(self):
        pass
        del self.store._server['dott_objects_test']

    def test_basic(self):
        pass