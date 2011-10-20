from src.server.commands.command import BaseCommand
from src.server.commands.exceptions import CommandError
from src.server.objects.exceptions import InvalidObjectId
from src.server.protocols.proxyamp import WhoConnectedCmd, DisconnectSessionsOnObjectCmd

class CmdExamine(BaseCommand):
    """
    Examines an object.
    """

    name = 'examine'
    aliases = ['ex', 'exa']

    def func(self, invoker, parsed_cmd):

        if not parsed_cmd.arguments:
            # No arguments means defaulting to 'here'.
            if not invoker.location:
                # This shouldn't ever happen, but...
                raise CommandError('You appear to be nowhere. Bummer.')

            user_query = 'here'
        else:
            user_query = ' '.join(parsed_cmd.arguments)

        if not user_query:
            raise CommandError('You must specify an object to examine')

        try:
            obj_match = invoker.contextual_object_search(user_query)
        except InvalidObjectId:
            obj_match = None

        if not obj_match:
            raise CommandError('No matching object found')

        appearance = self.get_appearance(obj_match, invoker)

        invoker.emit_to(appearance)

    def get_appearance(self, obj_match, invoker):
        """
        Checks to see whether the invoker is an admin. If so, admins get
        a very nerdy examine display that shows an object's un-parsed
        name/description, and attributes. If the invoker is a normal player,
        this will simply return the normal description.

        :rtype: str
        :returns: The object's appearance, from the invoker's perspective.
        """
        if invoker.is_admin():
            return obj_match.get_examine_appearance(invoker)
        else:
            return obj_match.get_appearance(invoker)


class CmdGo(BaseCommand):
    """
    Attempts to traverse an exit.
    """
    name = 'go'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Go through which exit?')

        # Join all arguments together into one single string so we can
        # do a contextual search for the whole thing.
        full_arg_str = ' '.join(parsed_cmd.arguments)


        try:
            obj_to_traverse = invoker.contextual_object_search(full_arg_str)
        except InvalidObjectId:
            obj_to_traverse = None
        if not obj_to_traverse:
            raise CommandError("Destination unknown.")

        if not obj_to_traverse.base_type == 'exit':
            invoker.emit_to("That doesn't look like an exit.")

        obj_to_traverse.pass_object_through(invoker)


class CmdCommands(BaseCommand):
    """
    Lists a break-down of available commands. Takes into account your location's
    command table (if applicable), and admin status.
    """
    name = 'commands'

    def func(self, invoker, parsed_cmd):
        service = invoker._mud_service
        # Buffer to send to user.
        buffer = ''

        if invoker.is_admin():
            buffer += '\nGlobal Admin Commands:'
            buffer += self._buffer_command_table(service.global_admin_cmd_table)

        invoker.emit_to(buffer)

    def _buffer_command_table(self, table):
        buffer = ''
        for cmd in table.commands:
            buffer += ' %s' % cmd.name
        return buffer

class CmdLook(CmdExamine):
    """
    Synonymous with examine, aside from always getting the object's normal
    appearance, regardless of whether the player is an admin or not.
    """
    name = 'look'
    aliases = ['l']

    def get_appearance(self, obj_match, invoker):
        """
        The 'look' command always shows an object's normal appearance, despite
        whether the invoker is a player or admin.

        :rtype: str
        :returns: The object's appearance.
        """
        return obj_match.get_appearance(invoker)


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

        invoker.location.emit_to_contents(speech_str, exclude=[invoker])
        invoker.emit_to(self_str)


class CmdQuit(BaseCommand):
    """
    Disconnects from the game.
    """
    name = 'quit'

    def func(self, invoker, parsed_cmd):
        invoker.emit_to("Quitting...")

        service = invoker._mud_service
        # This asks the proxy to disconnect any sessions that are currently
        # controlling this object.
        service.proxyamp.callRemote(
            DisconnectSessionsOnObjectCmd,
            object_id=invoker.id,
        )
