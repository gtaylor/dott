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

        :rtype: tuple
        :returns: A tuple in the format of (grouped_hangars, flat_hangar_id_list).
            The first is a dict whose keys are in-space object IDs with the
            values being hangar objects. The latter is a flat list of hangar
            dockable IDs.
        """

        # Keys are in-space objects, values will eventually be their hangar objects.
        grouped_hangars = {}
        inspace_objs = self.get_contents()
        # Look through each object's DOCKABLE_IDS attribute to see what the
        # possibilities are.
        for obj in inspace_objs:
            obj_dockables = obj.attributes.get('DOCKABLE_IDS', [])
            if not obj_dockables:
                continue
            grouped_hangars[obj.id] = obj_dockables

        # This will be a flattened list of hangar IDs the ship can dock to.
        flat_hangar_id_list = []
        # Now go through the dict of grouped hangar IDs, convert them to
        # BaseObject sub-classes, and run some checks to make sure we can
        # dock there.
        for space_obj_id, hangar_ids in grouped_hangars.items():
            space_obj_hangar_objs = []
            for hangar_id in hangar_ids:
                hangar_obj = self.mud_service.object_store.get_object(hangar_id)
                if not hasattr(hangar_obj, 'get_launchto_location'):
                    # Probably not a hangar after all.
                    continue
                space_obj_hangar_objs.append(hangar_obj)
                flat_hangar_id_list.append(hangar_obj.id)

            if space_obj_hangar_objs:
                # We had found results for this in-space object. Replace its
                # old list of IDs with a list of objects.
                grouped_hangars[space_obj_id] = space_obj_hangar_objs
            else:
                # This object had no dockable matches. Delete its key.
                del grouped_hangars[space_obj_id]

        return grouped_hangars, flat_hangar_id_list


class InSpaceObject(ThingObject):
    """
    All free-floating objects in a solar system. These differ from a Place
    in that they may be interacted with.
    """

    display_name = "InSpaceObject"


class PlanetObject(InSpaceObject):
    """
    Planets are stationary objects in space that may be landed on.

    src.game.parents.space.solar_system.PlanetObject
    """

    @property
    def display_name(self):
        return self.name