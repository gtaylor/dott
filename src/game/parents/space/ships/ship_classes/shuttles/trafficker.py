from src.game.parents.space.ships.interior.bridge import SpaceShipBridgeObject
from src.game.parents.space.ships.ship_classes.shuttles.base import BaseShuttleSpaceShipObject


class TraffickerSpaceShipBridgeObject(SpaceShipBridgeObject):
    """
    Customized bridge.

    src.game.parents.space.ships.ship_classes.shuttles.trafficker.TraffickerSpaceShipBridgeObject
    """

    def get_description(self, *args, **kwargs):
        """
        A customized bridge description for the ship.
        """

        return (
            "The cockpit of the Trafficker is minimalistic and cramped. "
            "A large chair with controls situated in front is where the "
            "pilot sits, with two rows of two seats situated behind. Tiny "
            "windows are on either side of each row of seats, and a small "
            "ramped hatch is in the floor near the aft."
        )

    
class TraffickerSpaceShipObject(BaseShuttleSpaceShipObject):
    """
    A basic shuttle class ship.

    src.game.parents.space.ships.ship_classes.shuttles.trafficker.TraffickerSpaceShipObject
    """

    ship_type_name = 'Trafficker'
    ship_reference = 'TFK-1A'

    bridge_parent = 'src.game.parents.space.ships.shuttles.trafficker.TraffickerSpaceShipBridgeObject'
