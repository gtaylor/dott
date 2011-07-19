from src.game.commands import general
from src.server.commands.cmdtable import CommandTable

class GlobalCommandTable(CommandTable):
    """
    The standard, global command table.
    """
    def __init__(self, *args, **kwargs):
        super(GlobalCommandTable, self).__init__(*args, **kwargs)

        self.add_command(general.CmdLook())