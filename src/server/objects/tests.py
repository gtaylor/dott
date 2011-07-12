import unittest2
from src.server.objects.in_memory_store import InMemoryObjectStore
from src.server.config.in_memory_store import InMemoryConfigStore

class InMemoryObjectStoreTests(unittest2.TestCase):
    def setUp(self):
        self.config_store = InMemoryConfigStore(db_name='dott_config_test')
        self.store = InMemoryObjectStore(
            db_name='dott_objects_test',
            config_store=self.config_store)

    def tearDown(self):
        #pass
        del self.store._server['dott_objects_test']
        del self.config_store._server['dott_config_test']

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
        new_player_room = self.config_store.get_value('NEW_PLAYER_ROOM')
        self.assertNotEqual(new_player_room, None)

    def test_create_room(self):
        """
        Creates a room and double-checks some values.
        """
        parent_path = 'src.game.parents.base_objects.room.RoomObject'
        room = self.store.create_object(parent_path, name='Another room')
        # The _id attribute should have a value from CouchDB.
        self.assertIsInstance(room._id, basestring)
        # The room name should match what was given during creation.
        self.assertEqual('Another room', room.name)
