from src.server.commands.command import BaseCommand

class CmdLook(BaseCommand):
    """
    Preliminary way to get room descriptions.
    """
    name = 'look'
    aliases = ['l']

    def func(self, invoker, parsed_cmd):
        invoker.emit_to('WHO YOU LOOKIN AT?')

class CmdWho(BaseCommand):
    """
    A REALLY basic WHO list.
    """
    name = 'who'

    def func(self, invoker, parsed_cmd):
        session_mgr = invoker._session_manager
        sessions = session_mgr.get_sessions()

        retval = "Player\n"

        for session in sessions:
            retval += " %s\n" % session.account.username

        nplayers = len(sessions)
        if nplayers == 1:
            retval += 'One player logged in.'
        else:
            retval += '%d players logged in.' % nplayers

        invoker.emit_to(retval)