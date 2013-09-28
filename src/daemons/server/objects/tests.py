"""
Object store tests.
"""

from twisted.internet.defer import inlineCallbacks

import settings
from src.utils.test_utils import DottTestCase


#noinspection PyProtectedMember
class InMemoryObjectStoreTests(DottTestCase):
    """
    Testing of the ObjectStore storage backend.
    """

    @inlineCallbacks
    def test_create_room(self):
        """
        Creates a room and double-checks some values.
        """

        room = yield self.object_store.create_object(settings.ROOM_PARENT, name='Another room')
        # The id attribute should have a value from the DB.
        self.assertIsInstance(room.id, int)
        # The room name should match what was given during creation.
        self.assertEqual('Another room', room.name)

    @inlineCallbacks
    def test_global_name_search(self):
        """
        Tests the global_name_search method on the object store. Fuzzy
        name matching.
        """

        parent_path = settings.ROOM_PARENT
        room1 = yield self.object_store.create_object(parent_path, name='Some room')
        room2 = yield self.object_store.create_object(parent_path, name='Another room')
        room3 = yield self.object_store.create_object(parent_path, name='Funny room')

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

    @inlineCallbacks
    def test_find_exits_linked_to_obj(self):
        """
        Tests the find_exits_linked_to_obj() method, which does what the name
        says.
        """

        # Create a room that will have an exit.
        room1 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 1')
        # Create the room that will be linked to.
        room2 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 2')
        # Create an exit in room1 that points to room2.
        test_exit = yield self.object_store.create_object(
            settings.EXIT_PARENT,
            location_id=room1.id,
            destination_id=room2.id,
            name='Test Exit')
        # Get a list of all exits linked to room2.
        exits = self.object_store.find_exits_linked_to_obj(room2)
        # The first (and only) member should be the test exit.
        self.assertEqual(exits[0].id, test_exit.id)
        self.assertEqual(len(exits), 1)

    @inlineCallbacks
    def test_find_objects_in_zone(self):
        """
        Tests the find_objects_in_zone() method, which does what the name
        says.
        """

        room1 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 1')
        room2 = yield self.object_store.create_object(
            settings.ROOM_PARENT,
            name='Room 2',
            zone_id=room1.id,
        )
        members = self.object_store.find_objects_in_zone(room1)
        self.assertEqual(members[0].id, room2.id)
        self.assertEqual(len(members), 1)