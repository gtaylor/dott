from src.utils.test_utils import DottTestCase


class ParentLoaderTests(DottTestCase):

    def test_simple_load(self):
        loader = self.object_store.parent_loader

        parent = loader.load_parent('src.game.parents.base_objects.room.RoomObject')
        self.assertEqual(parent.__name__, 'RoomObject')