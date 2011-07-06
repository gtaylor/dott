import exocet

class ParentLoader(object):
    """
    Handles loading and caching parent classes.
    """
    def __init__(self):
        # The parent cache has keys matching the full path + class to the
        # parent, and the value being a reference to the class.
        self._parent_cache = {}

    def load_parent(self, parent_str):
        """
        Checks the parent cache for the presence of the requested parent class,
        loading it with exocet if it's missing. Returns a reference to the
        parent class once all is done.

        :param str parent_str: The full module + class Python path to the
            parent to load.
        :rtype: A sub-class of src.game.parents.base_objects.BaseObject
        :returns: The requested parent class.
        """
        if not self._parent_cache.has_key(parent_str):
            module_str, class_str = self._split_parent(parent_str)

            module = exocet.loadNamed('src.game.parents.base_objects.room',
                                      exocet.pep302Mapper)
            parent = getattr(module, class_str)

            self._parent_cache[parent_str] = parent
        return self._parent_cache[parent_str]

    def _split_parent(self, parent_str):
        """
        Given a full Python path to a parent class, returns a 

        :param str parent_str: The full Python path to the parent class.
        :rtype: tuple
        :returns: A tuple in the format of (path, class).
        """
        return parent_str.rsplit('.', 1)