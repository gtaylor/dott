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
