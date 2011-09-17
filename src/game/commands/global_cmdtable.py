from src.server.commands.cmdtable import CommandTable

from src.game.commands import general as general_cmds
from src.game.commands import staff as staff_cmds

class GlobalCommandTable(CommandTable):
    """
    The standard, global command table.
    """
    def __init__(self, *args, **kwargs):
        super(GlobalCommandTable, self).__init__(*args, **kwargs)

        self.add_command(general_cmds.CmdLook())
        self.add_command(general_cmds.CmdWho())
        self.add_command(general_cmds.CmdSay())
        self.add_command(general_cmds.CmdQuit())

        # Staff commands
        self.add_command(staff_cmds.CmdRestart())
        self.add_command(staff_cmds.CmdFind())
        self.add_command(staff_cmds.CmdDig())
        self.add_command(staff_cmds.CmdTeleport())