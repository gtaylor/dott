from src.server.commands.command import BaseCommand

class CmdLook(BaseCommand):
    name = 'look'
    aliases = ['l']

    def func(self, parsed_cmd):
        print "LOOK!"
        pass