"""
Staff commands.
"""
from src.server.commands.command import BaseCommand

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
            invoker.emit_to('@find requires a name to search for.')
            return

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
            invoker.emit_to('@dig requires a name for the new room.')
            return

        room_parent = 'src.game.parents.base_objects.room.RoomObject'
        new_room = mud_service.object_store.create_object(
            room_parent,
            name=name_str,
        )
        invoker.emit_to('You have dug a new room: %s(%s)' % (
            new_room.name,
            new_room.id,
        ))
