from src.server.commands.command import Command

class CmdLook(Command):
    name = 'look'
    aliases = ['l']

    def func(self, parsed_cmd):
        print "LOOK!"
        pass