from src.utils.test_utils import DottTestCase

class InMemoryObjectStoreTests(DottTestCase):
    def test_starter_room_creation(self):
        """
        Makes sure the default DB is created with one room. Check some
        of the default values on it.
        """
        num_objects = len(self.object_store._objects)
        # There should only be one object at this point.
        self.assertEqual(num_objects, 1)

        # Get the starter room instance.
        id, room = self.object_store._objects.items()[0]
        # It should have been created with the standard room parent.
        self.assertEqual(room.parent, 'src.game.parents.base_objects.room.RoomObject')
        new_player_room = self.config_store.get_value('NEW_PLAYER_ROOM')
        self.assertNotEqual(new_player_room, None)

    def test_create_room(self):
        """
        Creates a room and double-checks some values.
        """
        parent_path = 'src.game.parents.base_objects.room.RoomObject'
        room = self.object_store.create_object(parent_path, name='Another room')
        # The _id attribute should have a value from CouchDB.
        self.assertIsInstance(room._id, basestring)
        # The room name should match what was given during creation.
        self.assertEqual('Another room', room.name)
