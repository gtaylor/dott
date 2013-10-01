from src.game.parents.base_objects.room import RoomObject
from src.game.parents.base_objects.thing import ThingObject


class SolarSystemObject(RoomObject):
    """
    Represents a solar system that may contain InSpaceObjects.

    src.game.parents.space.solar_system.SolarSystemObject
    """

    def get_places_obj_list(self):
        """
        Returns all warpable places in the solar system as a list.

        :rtype: list
        :returns: A list of :py:class:`SolarSystemPlaceObject` sub-classes.
        """

        return [
            obj for obj in self.get_contents()
            if isinstance(obj, SolarSystemPlaceObject)
        ]


class SolarSystemPlaceObject(ThingObject):
    """
    An object in space that may be warped to. These are more or less 'rooms'
    within the solar system.

    src.game.parents.space.solar_system.SolarSystemPlaceObject
    """

    def get_solar_system_obj(self):
        """
        Determines which solar system this place is in.

        :rtype: SolarSystemObject or ``None``
        :returns: The solar system the place is in, or ``None`` if we can't
            figure it out.
        """

        if self.location:
            return self.location

    def get_dockable_obj_list(self, invoker_ship):
        """
        Return a list of RoomHangarObject or ThingHangarObject objects that
        the invoking ship can dock/land in.

        :rtype: list
        :returns: A list of HangarMixin sub-classed instances that are dockable.
        """

        zone_members = self.mud_service.object_store.find_objects_in_zone(self)
        dockable_objs = []
        for obj in zone_members:
            if hasattr(obj, 'get_launchto_location'):
                dockable_objs.append(obj)
        # TODO: Factor in friendly ships with hangars.
        return dockable_objs


class PlanetObject(SolarSystemPlaceObject):
    """
    Planets are stationary objects in space that may be landed on.

    src.game.parents.space.solar_system.PlanetObject
    """

    pass


class InSpaceObject(ThingObject):
    """
    All free-floating objects in a solar system. These differ from a Place
    in that they may be interacted with.
    """

    display_name = "InSpaceObject"