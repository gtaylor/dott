from src.utils.test_utils import DottTestCase

class BaseObjectTests(DottTestCase):
    """
    Testing of the InMemoryObjectStore storage backend.
    """
    # Here for convenient reference.
    ROOM_PARENT = 'src.game.parents.base_objects.room.RoomObject'
    THING_PARENT = 'src.game.parents.base_objects.thing.ThingObject'

    def test_contents(self):
        """
        Tests object contents calculations.
        """
        room = self.object_store.create_object(self.ROOM_PARENT, name='A room')
        # Create a thing in the room.
        thing = self.object_store.create_object(
            self.THING_PARENT,
            location_id=room.id,
            name='Thing')
        # Get the list of objects that are within the room.
        contents = room.get_contents()
        # Contents should just be ``thing``, which was created inside the room.
        self.assertListEqual(contents, [thing])

    def test_set_location(self):
        """
        Tests the object's set_location function
        """

        # Create the rooms
        room1 = self.object_store.create_object(self.ROOM_PARENT, name='Room 1')
        room2 = self.object_store.create_object(self.ROOM_PARENT, name='Room 2')
        # Create a thing in Room 1
        thing = self.object_store.create_object(
            self.THING_PARENT,
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


class ThingObjectTests(DottTestCase):
    """
    Testing of the ThingObject class
    """
    # Here for convenient reference.
    ROOM_PARENT = 'src.game.parents.base_objects.room.RoomObject'
    THING_PARENT = 'src.game.parents.base_objects.thing.ThingObject'

    def test_base_type(self):
        """
        Tests the object's base type property
        """


        room = self.object_store.create_object(self.ROOM_PARENT, name='A room')
        # Create a thing in the room.
        thing = self.object_store.create_object(
            self.THING_PARENT,
            location_id=room.id,
            name='Thing')

        self.assertEqual(thing.base_type, 'thing')