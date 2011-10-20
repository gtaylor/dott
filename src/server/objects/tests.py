from src.utils.test_utils import DottTestCase

class InMemoryObjectStoreTests(DottTestCase):
    """
    Testing of the InMemoryObjectStore storage backend.
    """
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
        self.assertEqual(room.parent, self.ROOM_PARENT)

    def test_create_room(self):
        """
        Creates a room and double-checks some values.
        """
        parent_path = self.ROOM_PARENT
        room = self.object_store.create_object(parent_path, name='Another room')
        # The _id attribute should have a value from CouchDB.
        self.assertIsInstance(room.id, basestring)
        # The room name should match what was given during creation.
        self.assertEqual('Another room', room.name)

    def test_global_name_search(self):
        """
        Tests the global_name_search method on the object store. Fuzzy
        name matching.
        """
        parent_path = self.ROOM_PARENT
        room1 = self.object_store.create_object(parent_path, name='Some room')
        room2 = self.object_store.create_object(parent_path, name='Another room')
        room3 = self.object_store.create_object(parent_path, name='Funny room')

        # Search for 'some', we should have room1 as the sole result.
        matches1 = self.object_store.global_name_search('some')
        num_found = 0
        for match in matches1:
            if room1 == match:
                num_found += 1
        self.assertEqual(num_found, 1)

        # Search for 'room', which should yield three results.
        matches2 = self.object_store.global_name_search('room')
        num_found = 0
        for match in matches2:
            if room1 == match or room2 == match or room3 == match:
                num_found += 1
        self.assertEqual(num_found, 3)

    def test_find_exits_linked_to_obj(self):
        """
        Tests the find_exits_linked_to_obj() method, which does what the name
        says.
        """
        room1 = self.object_store.create_object(self.ROOM_PARENT, name='Room 1')
        room2 = self.object_store.create_object(self.ROOM_PARENT, name='Room 2')
        test_exit = self.object_store.create_object(
            self.EXIT_PARENT,
            location_id=room1.id,
            destination_id=room2.id,
            name='Test Exit')
        exits = self.object_store.find_exits_linked_to_obj(room2)
        self.assertEqual(exits[0], test_exit)
