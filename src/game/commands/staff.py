"""
Staff commands.
"""
from src.server.commands.command import BaseCommand

class CmdRestart(BaseCommand):
    """
    Shuts the MUD server down silently. Supervisor restarts it after noticing
    the exit, and most users will never notice since the proxy maintains
    their connections.
    """
    name = '@restart'

    def func(self, invoker, parsed_cmd):
        invoker.emit_to("Restarting...")
        mud_service = invoker._mud_service
        mud_service.shutdown()
