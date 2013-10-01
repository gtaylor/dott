"""
General commands that are available to everyone.
"""

import json

import settings
from src.daemons.server.commands.command import BaseCommand
from src.daemons.server.commands.exceptions import CommandError
from src.daemons.server.protocols.proxyamp import WhoConnectedCmd, DisconnectSessionsOnObjectCmd


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
            raise CommandError('You must specify an object to examine.')

        obj_match = invoker.contextual_object_search(user_query)
        if not obj_match:
            raise CommandError('No matching object found.')

        appearance = self.get_appearance(obj_match, invoker)

        invoker.emit_to(appearance)

    def get_appearance(self, obj, invoker):
        """
        Checks to see whether the invoker is an admin. If so, admins get
        a very nerdy examine display that shows an object's un-parsed
        name/description, and attributes. If the invoker is a normal player,
        this will simply return the normal description.

        :rtype: str
        :returns: The object's appearance, from the invoker's perspective.
        """

        if invoker.is_admin():
            return self.get_examine_appearance(obj, invoker)
        else:
            return obj.get_appearance(invoker)

    def get_examine_appearance(self, obj, invoker):
        """
        Shows the object as it were examined.
        """

        attributes_str = ' Parent: %s (%s)\n' % (obj.parent, obj.base_type)

        if obj.aliases:
            attributes_str += ' Aliases: %s\n' % ', '.join(obj.aliases)

        if obj.location:
            attributes_str += ' Location: %s\n' % obj.location.get_appearance_name(invoker)

        if obj.zone:
            attributes_str += ' Zone: %s\n' % obj.zone.get_appearance_name(invoker)

        attributes_str += ' Description: %s\n' % obj.description

        if obj.internal_description:
            attributes_str += ' Internal Description: %s\n' % obj.internal_description

        if obj.attributes:
            attributes_str += '\n### ATTRIBUTES ###\n'
            attributes_str += json.dumps(obj.attributes, indent=3)

        name = obj.get_appearance_name(invoker=invoker)
        return "%s\n%s" % (name, attributes_str)


class CmdGo(BaseCommand):
    """
    Attempts to traverse an exit.
    """
    name = 'go'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Go through which exit?')

        obj_to_traverse = invoker.contextual_object_search(parsed_cmd.argument_string)
        if not obj_to_traverse:
            raise CommandError("Destination unknown.")

        if not obj_to_traverse.base_type == 'exit':
            invoker.emit_to("That doesn't look like an exit.")

        obj_to_traverse.pass_object_through(invoker)


class CmdEnter(BaseCommand):
    """
    Attempts to enter an object.
    """
    name = 'enter'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Enter what?')

        obj_to_enter = invoker.contextual_object_search(parsed_cmd.argument_string)
        if not obj_to_enter:
            raise CommandError("You look around, but can't find it.")

        can_enter, cant_enter_msg = obj_to_enter.can_object_enter(invoker)
        if not can_enter:
            raise CommandError(cant_enter_msg)

        # Determine where entering the object puts us.
        enter_to = obj_to_enter.determine_enter_destination(invoker)
        # Use the original object's name for the user message.
        enter_to_name = obj_to_enter.get_appearance_name(invoker)
        invoker.emit_to("You enter %s" % enter_to_name)
        invoker.move_to(enter_to)


class CmdLeave(BaseCommand):
    """
    Attempts to leave an object.
    """

    name = 'leave'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        location = invoker.location
        can_leave, cant_leave_msg = location.can_object_leave(invoker)
        if not can_leave:
            raise CommandError(cant_leave_msg)

        # Determine where leaving the object puts us.
        leave_to = location.determine_leave_destination(invoker)
        # Use the original object's name for the user message.
        leave_from_name = location.get_appearance_name(invoker)
        invoker.emit_to("You leave %s" % leave_from_name)
        invoker.move_to(leave_to)


class CmdCommands(BaseCommand):
    """
    Lists a break-down of available commands. Takes into account your location's
    command table (if applicable), and admin status.
    """

    name = 'commands'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        service = invoker.mud_service
        # Buffer to send to user.
        buf = ''

        if invoker.is_admin():
            buf += '\nGlobal Admin Commands:'
            buf += self._buffer_command_table(
                service.global_admin_cmd_table
            )

        buf += '\nGlobal Commands:'
        buf += self._buffer_command_table(
            service.global_cmd_table
        )

        location = invoker.location
        if location:
            if invoker.is_admin() and location.local_admin_command_table:
                buf += '\nLocal Admin Commands:'
                buf += self._buffer_command_table(
                    location.local_admin_command_table
                )

            if location.local_command_table:
                buf += '\nLocal Commands:'
                buf += self._buffer_command_table(
                    location.local_command_table
                )

        invoker.emit_to(buf)

    def _buffer_command_table(self, table):
        """
        Given a CommandTable instance, return a string that lists the commands
        in the table.

        :param CommandTable table: The command table whose commands to list.
        :rtype: str
        :returns: A string list of commands in the table.
        """

        buf = ''
        for cmd in table.commands:
            buf += ' %s' % cmd.name
        return buf


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

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        """
        The proxy has all of the details on who is connected, so the mud server
        has to ask. This is handled through a deferred and a callback.
        """

        service = invoker.mud_service
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
        # The sentence to speak.
        speech = u' '.join(parsed_cmd.arguments)
        # Presentational arrangement for other neighboring objects to see.
        speech_str = u"%s says '%s'" % (invoker.name, speech)
        # What the invoker sees.
        self_str = u"You say '%s'" % speech

        invoker.location.emit_to_contents(speech_str, exclude=[invoker])
        invoker.emit_to(self_str)


class CmdQuit(BaseCommand):
    """
    Disconnects from the game.
    """

    name = 'quit'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        invoker.emit_to("Quitting...")

        service = invoker.mud_service
        # This asks the proxy to disconnect any sessions that are currently
        # controlling this object.
        service.proxyamp.callRemote(
            DisconnectSessionsOnObjectCmd,
            object_id=invoker.id,
        )


class CmdVersion(BaseCommand):
    """
    Shows the dott version identifier. Currently a git commit hash.
    """

    name = 'version'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        buf = "-" * 78
        buf += "\n %s version %s\n" % (
            settings.GAME_NAME,
            settings.VERSION
        )
        buf += "-" * 78
        invoker.emit_to(buffer)