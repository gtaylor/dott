from src.server.commands.cmdtable import CommandTable
from src.server.commands.command import BaseCommand
from src.game.parents.space.ships.interior.base import SpaceShipInteriorObject

class CmdLaunch(BaseCommand):
    """
    Launches the ship into space from a hangar.
    """
    name = 'launch'

    def func(self, invoker, parsed_cmd):
        mud_service = invoker._mud_service

        invoker.emit_to('Soon!')


class ShipBridgeCommandTable(CommandTable):
    def __init__(self, *args, **kwargs):
        super(ShipBridgeCommandTable, self).__init__(*args, **kwargs)

        self.add_command(CmdLaunch())


class SpaceShipBridgeObject(SpaceShipInteriorObject):
    """
    Ships are controlled from the bridge, regardless of size. Smaller ships
    call this a cockpit.
    """
    def _get_command_table(self):
        """
        Sets the command table to the bridge.

        :rtype: src.server.commands.cmdtable.CommandTable
        :returns: A correctly instantiated CommandTable object.
        """
        return ShipBridgeCommandTable(self._mud_service)