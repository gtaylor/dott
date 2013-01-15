from src.daemons.server.parent_loader.exceptions import InvalidParent

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
        loading it with __import__ if it's missing. Returns a reference to the
        parent class once all is done.

        :param str parent_str: The full module + class Python path to the
            parent to load.
        :rtype: A sub-class of src.game.parents.base_objects.BaseObject
        :returns: The requested parent class.
        :raises: :py:exc:`src.server.parent_loader.exceptions.InvalidParent`
            when an invalid parent is specified.
        """
        if not self._parent_cache.has_key(parent_str):
            # __import__ doesn't play nicely with class names within the
            # module you're importing. Split the parent class off from the
            # module path.
            try:
                module_str, parent_class = parent_str.rsplit('.', 1)
            except ValueError:
                raise InvalidParent(
                    'Attempted to load invalid parent: %s' % parent_str
                )

            # This imports the top-level src module, from which we have to
            # iterate through sub-modules to eventually get to what we want.
            # For example, src -> game -> parents -> base_objects.
            try:
                mod = __import__(module_str)
            except ImportError:
                raise InvalidParent(
                    'Attempted to load invalid parent: %s' % parent_str
                )
            components = module_str.split('.')
            for comp in components[1:]:
                # Enhance. ENHANCE!
                mod = getattr(mod, comp)

            # Finally, we're at the lowest module in the python module
            # path. Get the parent class from this.
            try:
                self._parent_cache[parent_str] = getattr(mod, parent_class)
            except AttributeError:
                raise InvalidParent(
                    'Attempted to load invalid parent: %s' % parent_str
                )
        return self._parent_cache[parent_str]
