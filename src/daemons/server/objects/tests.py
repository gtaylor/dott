"""
Object store tests.
"""

from twisted.internet.defer import inlineCallbacks, returnValue

import settings
from src.utils.test_utils import DottTestCase
from src.daemons.server.objects.exceptions import ObjectHasZoneMembers, NoSuchObject


#noinspection PyProtectedMember
class GeneralObjectStoreTests(DottTestCase):
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


class ZoneTests(DottTestCase):
    """
    Testing of the ObjectStore storage backend.
    """

    @inlineCallbacks
    def setUp(self):
        yield super(ZoneTests, self).setUp()

        self.zmo = yield self.object_store.create_object(settings.ROOM_PARENT, name='ZMO')
        self.room2 = yield self.object_store.create_object(
            settings.ROOM_PARENT,
            name='Room 2',
            zone_id=self.zmo.id,
        )
        self.room3 = yield self.object_store.create_object(
            settings.ROOM_PARENT,
            name='Room 3',
            zone_id=self.zmo.id,
        )

    def test_find_objects_in_zone(self):
        """
        Tests the find_objects_in_zone() method, which does what the name
        says.
        """

        members = self.object_store.find_objects_in_zone(self.zmo)
        member_ids = [self.room2.id, self.room3.id]

        self.assertEqual(len(members), 2)
        for member in members:
            self.assertTrue(member.id in member_ids)

    @inlineCallbacks
    def test_zmo_razing(self):
        """
        Makes sure that razing a ZMO destroys all members and the ZMO itself.
        """

        try:
            yield self.zmo.destroy()
            self.fail("Shouldn't be able to delete a ZMO with members.")
        except ObjectHasZoneMembers:
            pass
        yield self.object_store.raze_zone(self.zmo)

        # Make sure everything was actually destroyed.
        self.assertRaises(NoSuchObject, self.object_store.get_object, self.zmo.id)
        self.assertRaises(NoSuchObject, self.object_store.get_object, self.room2.id)
        self.assertRaises(NoSuchObject, self.object_store.get_object, self.room3.id)

    @inlineCallbacks
    def test_zmo_emptying(self):
        """
        Tests the emptying of a ZMO's members.
        """

        yield self.object_store.empty_out_zone(self.zmo)
        members = self.object_store.find_objects_in_zone(self.zmo)
        self.assertEqual(len(members), 0)
        # This shouldn't throw an exception now that all members are un-set.
        yield self.zmo.destroy()