from src.server.commands.command import BaseCommand
from src.server.protocols.proxyamp import WhoConnectedCmd

class CmdLook(BaseCommand):
    """
    Preliminary way to get room descriptions.
    """
    name = 'look'
    aliases = ['l']

    def func(self, invoker, parsed_cmd):
        if not invoker.location:
            invoker.emit_to('You appear to be nowhere. Bummer.')

        invoker.emit_to(invoker.location.get_appearance(invoker=invoker))


class CmdWho(BaseCommand):
    """
    A REALLY basic WHO list.
    """
    name = 'who'

    def func(self, invoker, parsed_cmd):
        """
        The proxy has all of the details on who is connected, so the mud server
        has to ask. This is handled through a deferred and a callback.
        """
        service = invoker._mud_service
        deferred = service.proxyamp.callRemote(WhoConnectedCmd)
        deferred.addCallback(self._wholist_callback, invoker)

    def _wholist_callback(self, results, invoker):
        """
        Once the proxy gets back to us on who is connected, this callback
        triggers.

        :param dict results: The details returned by the proxy.
        :param PlayerObject invoker: The player who ran the command.
        """
        accounts = results['accounts']

        retval = "Player\n"

        for account in accounts:
            retval += " %s\n" % account

        nplayers = len(accounts)
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