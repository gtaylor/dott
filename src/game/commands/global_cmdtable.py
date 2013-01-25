from src.daemons.server.commands.cmdtable import CommandTable

from src.game.commands import general as general_cmds
from src.game.commands import staff as staff_cmds


class GlobalCommandTable(CommandTable):
    """
    The standard, global command table.
    """
    commands = [
        general_cmds.CmdCommands(),
        general_cmds.CmdEnter(),
        general_cmds.CmdExamine(),
        general_cmds.CmdGo(),
        general_cmds.CmdLeave(),
        general_cmds.CmdLook(),
        general_cmds.CmdQuit(),
        general_cmds.CmdSay(),
        general_cmds.CmdVersion(),
        general_cmds.CmdWho(),
    ]


class GlobalAdminCommandTable(CommandTable):
    """
    Global command table for admin players.
    """
    commands = [
        staff_cmds.CmdAlias(),
        staff_cmds.CmdRestart(),
        staff_cmds.CmdFind(),
        staff_cmds.CmdCreate(),
        staff_cmds.CmdDig(),
        staff_cmds.CmdTeleport(),
        staff_cmds.CmdDescribe(),
        staff_cmds.CmdDestroy(),
        staff_cmds.CmdName(),
        staff_cmds.CmdOpen(),
        staff_cmds.CmdParent(),
        staff_cmds.CmdSet(),
        staff_cmds.CmdUnlink(),
        staff_cmds.CmdLink(),
        staff_cmds.CmdZone(),
    ]