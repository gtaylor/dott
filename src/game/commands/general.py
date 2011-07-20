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


class CmdSay(BaseCommand):
    """
    Communicate with people in the same room as you.
    """
    name = 'say'

    def func(self, invoker, parsed_cmd):
        # The contents of the object's current location.
        neighbors = invoker.location.get_contents()

        # The sentence to speak.
        speech = u' '.join(parsed_cmd.arguments)
        # Presentational arrangement for other neighboring objects to see.
        speech_str = u"%s says '%s'" % (invoker.name, speech)
        # What the invoker sees.
        self_str = u"You say '%s'" %  speech

        for neighbor in neighbors:
            if neighbor is not invoker:
                neighbor.emit_to(speech_str)
            else:
                invoker.emit_to(self_str)


class CmdQuit(BaseCommand):
    """
    Disconnects from the game.
    """
    name = 'quit'

    def func(self, invoker, parsed_cmd):
        sessions = invoker.get_connected_sessions()
        for session in sessions:
            invoker.emit_to("Disconnecting...")
            session.disconnect_client()