"""
Staff commands.
"""
from src.server.commands.command import BaseCommand

class CmdReload(BaseCommand):
    """
    Reloads most of the server code.
    """
    name = '@reload'

    def func(self, invoker, parsed_cmd):
        invoker.emit_to("Reloading...")
        mud_service = invoker._mud_service
        mud_service.reload_components()
        invoker.emit_to("Reloading completed.")
