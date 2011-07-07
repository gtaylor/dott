class BaseObject(object):
    """
    This is the base parent for every in-game "object". Rooms, Players, and
    Things are all considered objects. Behaviors here are very low level.
    """
    def __init__(self, **kwargs):
        """
        :param dict kwargs: All objects are instantiated with the values from
            the DB as kwargs. Since the DB representation of all of an
            objects attributes is just a dict, this works really well.
        """
        # This stores all of the object's data. This includes core and
        # userspace attributes.
        self.odata = kwargs

        # The 'attributes' key in the odata dict contains userspace attributes,
        # which are "user" defined (user being the developer), rather than
        # the core attributes in the top level of the dict.
        if not self.odata.has_key('attributes'):
            # No attributes dict found, create one so it may be saved to the DB.
            self.odata['attributes'] = {}

    def __getattr__(self, name):
        """
        If the user requests an attribute that can't be found on an object,
        assume they're looking for a core attribute. They can also get at the
        userspace attributes.

        :param str name: The attribute the user is looking for.
        :returns: The requested value, pulled from :attrib:`odata`.
        :raises: AttributeError if no match is found in :attrib:`odata`.
        """
        try:
            return self.odata[name]
        except KeyError:
            raise AttributeError()

