"""
Staff commands.
"""
from src.game.parents.base_objects.player import PlayerObject
from src.game.parents.base_objects.room import RoomObject
from src.server.commands.command import BaseCommand
from src.server.commands.exceptions import CommandError
from src.server.objects.exceptions import InvalidObjectId

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


class CmdFind(BaseCommand):
    """
    Does a fuzzy name match for all objects in the DB. Useful for finding
    various objects.
    """
    name = '@find'

    def func(self, invoker, parsed_cmd):
        mud_service = invoker._mud_service

        search_str = ' '.join(parsed_cmd.arguments)

        if search_str.strip() == '':
            raise CommandError('@find requires a name to search for.')

        invoker.emit_to("\nSearching for: %s" % search_str)

        # Performs a global fuzzy name match. Returns a generator.
        matches = mud_service.object_store.global_name_search(search_str)

        # Buffer for returning everything at once.
        retval = ''
        match_counter = 0
        for match in matches:
            retval += '\n  #%s %s %s' % (
                match.id.ljust(6),
                match.base_type.ljust(8),
                match.name[:80]
            )
            match_counter += 1
        # Send the results in one burst.
        invoker.emit_to(retval)
        invoker.emit_to('\nMatches found: %d' % match_counter)


class CmdDig(BaseCommand):
    """
    Digs a new room.
    """
    name = '@dig'

    def func(self, invoker, parsed_cmd):
        mud_service = invoker._mud_service

        name_str = ' '.join(parsed_cmd.arguments)

        if name_str.strip() == '':
            raise CommandError('@dig requires a name for the new room.')

        room_parent = 'src.game.parents.base_objects.room.RoomObject'
        new_room = mud_service.object_store.create_object(
            room_parent,
            name=name_str,
        )
        invoker.emit_to('You have dug a new room: %s(#%s)' % (
            new_room.name,
            new_room.id,
        ))


class CmdTeleport(BaseCommand):
    """
    Moves an object from one place to another
    """
    name = '@teleport'
    aliases = ['@tel']

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Teleport what to where?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)
        # Start off assuming the first member is the object that is to
        # be teleported.
        obj_to_tel_str = equal_sign_split[0]

        if len(equal_sign_split) == 1:
            # No destination provided. Defaults target object to 'me', and
            # moves the single arg to the destination.
            obj_to_tel_str = 'me'
            # First (and only) arg becomes destination.
            destination_str = equal_sign_split[0]
        else:
            # A destination was provided, so use it.
            destination_str = equal_sign_split[1]

        try:
            obj_to_tel = invoker.contextual_object_search(obj_to_tel_str)
        except InvalidObjectId:
            obj_to_tel = None
        if not obj_to_tel:
            raise CommandError('Unable to find your target object to teleport.')

        try:
            destination = invoker.contextual_object_search(destination_str)
        except InvalidObjectId:
            destination = None
        if not destination:
            raise CommandError('Unable to find your destination.')

        if isinstance(obj_to_tel, RoomObject):
            raise CommandError('Rooms cannot be teleported')

        if obj_to_tel.id == destination.id:
            raise CommandError('Objects can not teleport inside themselves.')

        obj_to_tel.set_location(destination)
        invoker.execute_command('look')


class CmdDescribe(BaseCommand):
    """
    Sets an object's description.
    """
    name = '@describe'
    aliases = ['@desc']

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Describe what?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No description provided.')

        obj_to_desc_str = equal_sign_split[0]
        description = equal_sign_split[1]

        try:
            obj_to_desc = invoker.contextual_object_search(obj_to_desc_str)
        except InvalidObjectId:
            obj_to_desc = None
        if not obj_to_desc:
            raise CommandError('Unable to find your target object to describe.')

        invoker.emit_to('You describe %s' % obj_to_desc.get_appearance_name(invoker))
        obj_to_desc.description = description
        obj_to_desc.save()


class CmdName(BaseCommand):
    """
    Sets an object's name.
    """
    name = '@name'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Name what?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No name provided.')

        obj_to_desc_str = equal_sign_split[0]
        name = equal_sign_split[1]

        try:
            obj_to_desc = invoker.contextual_object_search(obj_to_desc_str)
        except InvalidObjectId:
            obj_to_desc = None
        if not obj_to_desc:
            raise CommandError('Unable to find your target object to name.')

        invoker.emit_to('You re-name %s' % obj_to_desc.get_appearance_name(invoker))
        obj_to_desc.name = name
        obj_to_desc.save()


class CmdDestroy(BaseCommand):
    """
    Destroys an object.
    """
    name = '@destroy'
    aliases = ['@dest', '@nuke']

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Name what?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No name provided.')

        obj_to_desc_str = equal_sign_split[0]
        name = equal_sign_split[1]

        try:
            obj_to_desc = invoker.contextual_object_search(obj_to_desc_str)
        except InvalidObjectId:
            obj_to_desc = None
        if not obj_to_desc:
            raise CommandError('Unable to find your target object to name.')

        invoker.emit_to('You re-name %s' % obj_to_desc.get_appearance_name(invoker))
        obj_to_desc.name = name
        obj_to_desc.save()