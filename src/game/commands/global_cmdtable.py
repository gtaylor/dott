import exocet
from src.server.commands.cmdtable import CommandTable
from src.utils import logger

class GlobalCommandTable(CommandTable):
    """
    The standard, global command table.
    """
    def __init__(self, *args, **kwargs):
        super(GlobalCommandTable, self).__init__(*args, **kwargs)

        general_cmds = exocet.loadNamed(
            'src.game.commands.general',
            exocet.pep302Mapper
        )
        staff_cmds = exocet.loadNamed(
            'src.game.commands.staff',
            exocet.pep302Mapper
        )

        self.add_command(general_cmds.CmdLook())
        self.add_command(general_cmds.CmdWho())
        self.add_command(general_cmds.CmdSay())
        self.add_command(general_cmds.CmdQuit())

        # Staff commands
        self.add_command(staff_cmds.CmdReload())

    def __del__(self):
        logger.info("GlobalCommandTable instance GC'd.")