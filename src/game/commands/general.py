from src.server.commands.command import BaseCommand

class CmdLook(BaseCommand):
    name = 'look'
    aliases = ['l']

    def func(self, invoker, parsed_cmd):
        invoker.emit_to('WHO YOU LOOKIN AT?')

class CmdWho(BaseCommand):
    name = 'who'

    def func(self, invoker, parsed_cmd):
        invoker.emit_to('WHO YOU LOOKIN AT?')