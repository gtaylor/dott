"""
This suite tests basic top-level parents.
"""
from twisted.internet.defer import inlineCallbacks

import settings
from src.game.parents.base_objects.thing import ThingObject
from src.daemons.server.objects.exceptions import InvalidObjectId
from src.utils.test_utils import DottTestCase


class BaseObjectTests(DottTestCase):
    """
    Testing of the ObjectStore storage backend.
    """

    @inlineCallbacks
    def test_contents(self):
        """
        Tests object contents calculations.
        """
        room = yield self.object_store.create_object(settings.ROOM_PARENT, name='A room')
        # Create a thing in the room.
        thing = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=room.id,
            name='Thing')
        # Get the list of objects that are within the room.
        contents = room.get_contents()
        # Contents should just be ``thing``, which was created inside the room.
        self.assertListEqual(contents, [thing])

    @inlineCallbacks
    def test_get_location(self):
        """
        Tests the objects' get_location function
        """

        obj1 = yield self.object_store.create_object(settings.ROOM_PARENT, name='obj1')
        self.assertEqual(obj1.get_location(), None)

        obj2 = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=obj1.id,
            name='obj2')
        self.assertEqual(obj2.get_location(), obj1)

    @inlineCallbacks
    def test_set_location(self):
        """
        Tests the object's set_location function
        """

        # Create the rooms
        room1 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 1')
        room2 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 2')
        # Create a thing in Room 1
        thing = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=room1.id,
            name='Thing')

        # Move the thing to Room 2 using the room object as reference
        thing.set_location(room2)
        # Thing should now be in Room 2
        self.assertEqual(room2, thing.get_location())
        # Move the thing back to Room 1 using the room's object id
        thing.set_location(room1.id)
        # thing should now be in Room 1
        self.assertEqual(room1, thing.get_location())

    @inlineCallbacks
    def test_contextual_object_search(self):
        """
        Tests the object's contextual_object_search function
        """

        # Create the rooms
        room1 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 1')
        #noinspection PyUnusedLocal
        room2 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 2')
        # Create a thing in Room 1
        smallthing = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=room1.id,
            name='Small Thing')
        bigthing = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=room1.id,
            name='Big Thing')
        keything = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=smallthing.id,
            name='Big Key Thing')

        # smallthing will be our reference point

        # 'me' should refer to smallthing
        self.assertEqual(smallthing, smallthing.contextual_object_search('me'))

        # 'here' should refer to room1
        self.assertEqual(room1, smallthing.contextual_object_search('here'))

        # #<id> should refer to an absolute id
        absid = '#%s' % str(room1.id)
        self.assertEqual(room1, smallthing.contextual_object_search(absid))

        # 'big' should refer to bigthing which is in the room with smallthing
        self.assertEqual(bigthing, smallthing.contextual_object_search('big'))

        # 'key' should refer to keything which is inside of smallthing
        self.assertEqual(keything, smallthing.contextual_object_search('key'))

    @inlineCallbacks
    def test_deletion_cleanup(self):
        """
        Whenever an object is deleted, any exits linking to it are destroyed.
        If any other objects had the condemned object set as their zone master,
        the zone value is wiped.
        """
        # This room will hold an exit to room2.
        room1 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 1')
        # The room to be linked to via exit in room1.
        room2 = yield self.object_store.create_object(settings.ROOM_PARENT, name='Room 2')
        # Create a third room to assist in zone deletion testing.
        room3 = yield self.object_store.create_object(
            settings.ROOM_PARENT,
            name='Room 3',
            zone_id=room1.id
        )
        # Create an exit in room1 that links to room2.
        test_exit = yield self.object_store.create_object(
            settings.EXIT_PARENT,
            location_id=room1.id,
            destination_id=room2.id,
            name='Test Exit')
        # This should the test_exit.
        yield room2.destroy()
        # Query the object store for the destroyed exit. Should fail due to it
        # being deleted.
        self.assertRaises(
            InvalidObjectId,
            self.object_store.get_object, test_exit.id)
        # Double-check that the zone was set correctly.
        self.assertEqual(room3.zone.id, room1.id)
        # This should wipe the zone on room3.
        yield room1.destroy()
        # Make sure room3's zone was wiped, since its zone master was destroyed.
        self.assertEqual(room3.zone, None)


class ThingObjectTests(DottTestCase):
    """
    Testing of the ThingObject class
    """

    @inlineCallbacks
    def test_base_type(self):
        """
        Tests the object's base type property
        """
        room = yield self.object_store.create_object(settings.ROOM_PARENT, name='A room')
        # Create a thing in the room.
        thing = yield self.object_store.create_object(
            settings.THING_PARENT,
            location_id=room.id,
            name='Thing')

        self.assertIsInstance(thing, ThingObject)