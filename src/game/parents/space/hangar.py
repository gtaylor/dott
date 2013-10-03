from src.game.parents.base_objects.room import RoomObject
from src.game.parents.base_objects.thing import ThingObject
from src.game.parents.space.solar_system import SolarSystemPlaceObject


class HangarMixin(object):
    """
    Contains hangar-specific stuff.
    """

    def get_inspace_obj(self):
        """
        Returns the object that this hangar is attached to in space. This will
        be used to move the ship to the correct place after launching, and
        etc.

        :rtype: SolarSystemPlaceObject (planet) or InSpaceObject (ship/station)
        :returns: The object that this hangar is attached to in space.
        """

        #noinspection PyUnresolvedReferences
        assert self.zone, "No zone set on Hangar."
        #noinspection PyUnresolvedReferences
        return self.zone

    def get_launchto_location(self):
        """
        Get the location that any ship launches from here lead to.

        :rtype: SolarSystemPlaceObject or None
        :returns: The SolarSystemPlaceObject sub-class that any ships launched
            from here will be moved to in space. If a None is returned, ships
            should not be able to launch.
        """

        return self.get_inspace_obj().location

    def get_solar_system_obj(self):
        """
        Determines which solar system the hangar is in.

        :rtype: SolarSystemObject or ``None``
        :returns: The solar system the hangar is in, or ``None`` if we can't
            figure it out.
        """

        launch_to = self.get_launchto_location()
        if launch_to:
            return launch_to.get_solar_system_obj()


class RoomHangarObject(RoomObject, HangarMixin):
    """
    A room-based hangar. Typically used on planets.

    src.game.parents.space.hangar.RoomHangarObject
    """

    pass


class ThingHangarObject(ThingObject, HangarMixin):
    """
    Thing-based hangar. More common within ships and space stations.

    src.game.parents.space.hangar.ThingHangarObject
    """

    pass