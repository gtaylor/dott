"""
Staff commands.
"""
from twisted.internet.defer import inlineCallbacks
from src.daemons.server.protocols.proxyamp import ShutdownProxyCmd
from src.daemons.server.commands.command import BaseCommand
from src.daemons.server.commands.exceptions import CommandError
from src.daemons.server.objects.exceptions import InvalidObjectId
from src.daemons.server.objects.parent_loader.exceptions import InvalidParent
from src.game.parents.base_objects.exit import ExitObject
from src.game.parents.base_objects.room import RoomObject

class CmdRestart(BaseCommand):
    """
    Shuts the MUD server down silently. Supervisor restarts it after noticing
    the exit, and most users will never notice since the proxy maintains
    their connections.

    To restart the MUD server::

        @restart
        -or-
        @restart mud

    To restart the proxy server::

        @restart proxy
    """
    name = '@restart'

    #noinspection PyUnusedLocal
    def func(self, invoker, parsed_cmd):
        mud_service = invoker._mud_service
        
        if not parsed_cmd.arguments or 'mud' in parsed_cmd.arguments:
            invoker.emit_to("Restarting MUD server...")
            mud_service.shutdown()

        if 'proxy' in parsed_cmd.arguments:
            invoker.emit_to("Restarting proxy server...")
            mud_service.proxyamp.callRemote(ShutdownProxyCmd)


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

        invoker.emit_to('\nSearching for "%s"' % search_str)

        # Performs a global fuzzy name match. Returns a generator.
        matches = mud_service.object_store.global_name_search(search_str)

        # Buffer for returning everything at once.
        retval = ''
        match_counter = 0
        for match in matches:
            retval += '\n  #%s %s %s' % (
                str(match.id).ljust(6),
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

    @inlineCallbacks
    def func(self, invoker, parsed_cmd):
        mud_service = invoker._mud_service

        name_str = ' '.join(parsed_cmd.arguments)

        if name_str.strip() == '':
            raise CommandError('@dig requires a name for the new room.')

        room_parent = 'src.game.parents.base_objects.room.RoomObject'
        new_room = yield mud_service.object_store.create_object(
            room_parent,
            name=name_str,
        )
        invoker.emit_to('You have dug a new room named "%s"' % (
            new_room.get_appearance_name(invoker),
        ))


class CmdCreate(BaseCommand):
    """
    Creates a new ThingObject, which can be @parent'd to something else.
    """
    name = '@create'

    @inlineCallbacks
    def func(self, invoker, parsed_cmd):
        mud_service = invoker._mud_service

        name_str = ' '.join(parsed_cmd.arguments)

        if name_str.strip() == '':
            raise CommandError('You must provide a name for the new Thing.')

        thing_parent = 'src.game.parents.base_objects.thing.ThingObject'
        new_thing = yield mud_service.object_store.create_object(
            thing_parent,
            name=name_str,
            location_id=invoker.location.id,
        )
        invoker.emit_to('You have created a new thing named "%s"' % (
            new_thing.get_appearance_name(invoker),
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

        # Move the object, forces a 'look' afterwards.
        obj_to_tel.move_to(destination)


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


class CmdZone(BaseCommand):
    """
    Sets an object's zone.
    """
    name = '@zone'

    @inlineCallbacks
    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Set the zone on what?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No zone provided.')

        obj_to_zone_str = equal_sign_split[0]
        try:
            obj_to_zone = invoker.contextual_object_search(obj_to_zone_str)
        except InvalidObjectId:
            obj_to_zone = None
        if not obj_to_zone:
            raise CommandError('Unable to find your target object to zone.')

        zone_obj_str = equal_sign_split[1]
        if not zone_obj_str:
            zone_obj = None
        else:
            try:
                zone_obj = invoker.contextual_object_search(zone_obj_str)
            except InvalidObjectId:
                zone_obj = None
            if not zone_obj:
                raise CommandError('Unable to find your zone master object.')

        obj_to_zone.zone = zone_obj
        yield obj_to_zone.save()

        if zone_obj:
            invoker.emit_to('You zone %s to %s' % (
                obj_to_zone.get_appearance_name(invoker),
                zone_obj.get_appearance_name(invoker),
            ))
        else:
            invoker.emit_to('You clear the zone (if any) on %s' % (
                    obj_to_zone.get_appearance_name(invoker),
            ))

class CmdParent(BaseCommand):
    """
    Changes an object's parent.
    """
    name = '@parent'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Re-parent what?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No parent provided.')

        obj_to_parent_str = equal_sign_split[0]
        parent_str = equal_sign_split[1]
        parent_str = self._substitute_aliased_parent(parent_str)

        if not parent_str:
            raise CommandError('No parent provided.')

        try:
            obj_to_parent = invoker.contextual_object_search(obj_to_parent_str)
        except InvalidObjectId:
            obj_to_parent = None
        if not obj_to_parent:
            raise CommandError('Unable to find your target object to re-parent.')

        mud_service = invoker._mud_service

        try:
            mud_service.object_store.parent_loader.load_parent(parent_str)
        except InvalidParent, exc:
            raise CommandError(exc.message)

        obj_to_parent.parent = parent_str
        obj_to_parent.save()

        obj_to_parent= mud_service.object_store.reload_object(obj_to_parent)

        invoker.emit_to('You re-parent %s' % (
            obj_to_parent.get_appearance_name(invoker),
        ))

    def _substitute_aliased_parent(self, parent_str):
        """
        Given a parent string, see if it matches one of the base parent
        types. If so, replace the aliased parent string with the full path
        to the parent.

        :param str parent_str: The parent string passed to @parent.
        :rtype: str
        :returns: The full path to the parent string, if an alias match was
            found. Otherwise, assume that ``parent_str`` is a full parent
            string, and doesn't need modification.
        """
        aliases = {
            'thing': 'src.game.parents.base_objects.thing.ThingObject',
            'room': 'src.game.parents.base_objects.room.RoomObject',
            'exit': 'src.game.parents.base_objects.exit.ExitObject',
            'player': 'src.game.parents.base_objects.player.PlayerObject',
            'admin': 'src.game.parents.base_objects.player.AdminPlayerObject',
        }
        return aliases.get(parent_str.lower(), parent_str)


class CmdAlias(BaseCommand):
    """
    Sets an object's full list of aliases in one shot.
    """
    name = '@alias'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Alias what?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No alias(es) provided.')

        obj_to_alias_str = equal_sign_split[0]
        aliases = equal_sign_split[1].split()

        try:
            obj_to_alias = invoker.contextual_object_search(obj_to_alias_str)
        except InvalidObjectId:
            obj_to_alias = None
        if not obj_to_alias:
            raise CommandError('Unable to find your target object to alias.')

        if not aliases:
            invoker.emit_to(
                'You clear all aliases on %s.' % (
                    obj_to_alias.get_appearance_name(invoker),
            ))
        else:
            invoker.emit_to(
                'You alias %s to: %s' % (
                    obj_to_alias.get_appearance_name(invoker),
                    ', '.join(aliases),
            ))
        obj_to_alias.aliases = aliases
        obj_to_alias.save()


class CmdDestroy(BaseCommand):
    """
    Destroys an object.
    """
    name = '@destroy'
    aliases = ['@dest', '@nuke']

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Destroy what?')

        # Join all arguments together into one single string so we can
        # do a contextual search for the whole thing.
        full_arg_str = ' '.join(parsed_cmd.arguments)


        try:
            obj_to_destroy = invoker.contextual_object_search(full_arg_str)
        except InvalidObjectId:
            obj_to_destroy = None
        if not obj_to_destroy:
            raise CommandError('Unable to find your target object to destroy.')

        invoker.emit_to('You destroy %s' % obj_to_destroy.get_appearance_name(invoker))
        obj_to_destroy.destroy()


class CmdOpen(BaseCommand):
    """
    Opens an exit.

    @open <alias/dir> <exit-name>
    @open <alias/dir> <exit-name>=<dest-dbref>
    """
    name = '@open'

    @inlineCallbacks
    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Open an exit named what, and to where?')

        if len(parsed_cmd.arguments) < 2:
            raise CommandError(
                'You must at least provide an alias and an exit name.'
            )

        alias_str = parsed_cmd.arguments[0]

        name_and_dest_str = ' '.join(parsed_cmd.arguments[1:])
        name_dest_split = name_and_dest_str.split('=', 1)

        exit_name = name_dest_split[0]

        if len(name_dest_split) > 1:
            dest_str = name_dest_split[1]
        else:
            dest_str = None

        if dest_str:
            try:
                destination = invoker.contextual_object_search(dest_str)
                destination_id = destination.id
            except InvalidObjectId:
                raise CommandError('Unable to find specified destination.')
        else:
            destination = None
            destination_id = None

        mud_service = invoker._mud_service
        exit_parent = 'src.game.parents.base_objects.exit.ExitObject'
        new_exit = yield mud_service.object_store.create_object(
            exit_parent,
            name=exit_name,
            location_id=invoker.location.id,
            destination_id=destination_id,
            aliases=[alias_str],
        )

        if destination:
            invoker.emit_to(
                'You have opened a new exit to %s named "%s"' % (
                    destination.get_appearance_name(invoker),
                    new_exit.get_appearance_name(invoker),
                )
            )
        else:
            invoker.emit_to(
                'You have opened a new exit (with no destination) named "%s"' % (
                    new_exit.get_appearance_name(invoker)
                )
            )


class CmdUnlink(BaseCommand):
    """
    Removes an exit's destination.
    """
    name = '@unlink'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Unlink which exit?')

        # Join all arguments together into one single string so we can
        # do a contextual search for the whole thing.
        full_arg_str = ' '.join(parsed_cmd.arguments)

        try:
            obj_to_unlink = invoker.contextual_object_search(full_arg_str)
        except InvalidObjectId:
            obj_to_unlink = None
        if not obj_to_unlink:
            raise CommandError('Unable to find your target exit to unlink.')

        if not isinstance(obj_to_unlink, ExitObject):
            raise CommandError('You may only unlink exits.')

        invoker.emit_to(
            'You unlink %s' % obj_to_unlink.get_appearance_name(invoker)
        )

        obj_to_unlink.destination = None
        obj_to_unlink.save()


class CmdLink(BaseCommand):
    """
    Links an exit to a destination, typically a room or thing.
    """
    name = '@link'

    def func(self, invoker, parsed_cmd):
        if not parsed_cmd.arguments:
            raise CommandError('Link which exit?')

        # Join all arguments together into one single string so we can
        # split be equal sign.
        full_arg_str = ' '.join(parsed_cmd.arguments)
        # End up with a list of one or two members. Splits around the
        # first equal sign found.
        equal_sign_split = full_arg_str.split('=', 1)

        if len(equal_sign_split) == 1:
            raise CommandError('No destination provided.')

        obj_to_link_str = equal_sign_split[0]
        try:
            obj_to_link = invoker.contextual_object_search(obj_to_link_str)
        except InvalidObjectId:
            obj_to_link = None
        if not obj_to_link:
            raise CommandError('Unable to find your target exit to link.')

        if not isinstance(obj_to_link, ExitObject):
            raise CommandError('You may only link exits.')

        destination_obj_str = equal_sign_split[1]
        try:
            destination_obj = invoker.contextual_object_search(destination_obj_str)
        except InvalidObjectId:
            destination_obj = None
        if not destination_obj:
            raise CommandError('Unable to find the specified destination.')

        if isinstance(destination_obj, ExitObject):
            raise CommandError("You can't link to other exits.")

        invoker.emit_to(
            'You link %s to %s.' % (
                obj_to_link.get_appearance_name(invoker),
                destination_obj.get_appearance_name(invoker),
            )
        )
        obj_to_link.destination = destination_obj
        obj_to_link.save()