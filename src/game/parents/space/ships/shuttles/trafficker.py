from src.game.parents.space.ships import defines as ship_defines
from src.game.parents.space.ships.base import BaseSpaceShipObject
from src.game.parents.space.ships.interior.bridge import SpaceShipBridgeObject

class TraffickerSpaceShipBridgeObject(SpaceShipBridgeObject):
    """
    Customized bridge.
    """
    def get_description(self, *args, **kwargs):
        """
        A customized bridge description for the ship.
        """
        return "The cockpit of the Trafficker is minimalistic and cramped. " \
               "A large chair with controls situated in front is where the " \
               "pilot sits, with two rows of two seats situated behind. Tiny " \
               "windows are on either side of each row of seats, and a small " \
               "ramped hatch is in the floor near the aft."

    
class TraffickerSpaceShipObject(BaseSpaceShipObject):
    """
    A basic shuttle class ship.
    """
    ship_type_name = 'Trafficker'
    ship_class = ship_defines.SHIP_CLASS_SHUTTLE

    bridge_parent = 'src.game.parents.space.ships.shuttles.trafficker.TraffickerSpaceShipBridgeObject'
