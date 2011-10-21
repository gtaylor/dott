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
        return self.zone

    def get_launchto_location(self):
        """
        Get the location that any ship launches from here lead to.

        :rtype: SolarSystemPlaceObject or None
        :returns: The SolarSystemPlaceObject sub-class that any ships launched
            from here will be moved to in space. If a None is returned, ships
            should not be able to launch.
        """
        inspace_obj = self.get_inspace_obj()
        launch_loc_is_place_obj = isinstance(inspace_obj, SolarSystemPlaceObject)
        if launch_loc_is_place_obj:
            return inspace_obj

        # This is a station or a ship. Take its location.
        containing_ship_location = launch_loc_is_place_obj.location
        # Determine whether the ship/station is somewhere ships can launch from.
        can_launch = isinstance(containing_ship_location, SolarSystemPlaceObject)
        if can_launch:
            return containing_ship_location

        return None

class RoomHangarObject(RoomObject, HangarMixin):
    """
    A room-based hangar.
    """
    pass

class ThingHangarObject(ThingObject, HangarMixin):
    """
    Thing-based hangar. More common within ships and space stations.
    """
    pass