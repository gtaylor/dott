from src.utils.test_utils import DottTestCase
from src.server.commands.parser import CommandParser, ParsedCommand
from src.server.commands.cmdtable import CommandTable, DuplicateCommandException
from src.server.commands.command import BaseCommand

class CommandTableTests(DottTestCase):
    def setUp(self):
        self.table = CommandTable()

    def tearDown(self):
        del self.table

    def test_add_and_lookup(self):
        """
        Tests some simple success cases. A fake command is added to the
        command table, we perform some lookups.
        """
        # Create a fake command to add to the command table.
        cmd = BaseCommand()
        # This is the full name for the command.
        cmd.name = 'test'
        # The command can also be called with these values.
        cmd.aliases = ['t']
        # Add command to command table.
        self.table.add_command(cmd)

        # Perform a name-based lookup for the command. Result should be the
        # BaseCommand() instance we created earlier.
        self.assertIs(self.table.match_name('test'), cmd)
        # Same as above, but this time look for alias matches.
        self.assertIs(self.table.match_alias('t'), cmd)

        # Now take a step back and create a fake parsed command (from the user).
        # This is as if a user typed 'test'.
        parsed = ParsedCommand('test', [], [])
        # Hand the command off to the command table and ask it to return
        # a match, if there is one. This should match the previously created
        # test command.
        self.assertIs(self.table.lookup_command(parsed), cmd)
        # Now make the input something that definitely isn't in the command
        # table. The return value should be None, meaning no match.
        parsed.command_str = 'invalid'
        self.assertEqual(self.table.lookup_command(parsed), None)

    def test_add_duplicate_name(self):
        """
        Tries to add a duplicate (name) command.
        """
        cmd = BaseCommand()
        cmd.name = 'test'
        self.table.add_command(cmd)

        cmd2 = BaseCommand()
        cmd2.name = 'test'
        # This is a duplicate, should raise exception.
        self.assertRaises(DuplicateCommandException, self.table.add_command, cmd2)

    def test_add_duplicate_alias(self):
        """
        Tries to add a duplicate (alias) command.
        """
        cmd = BaseCommand()
        cmd.name = 'cmd'
        cmd.aliases = ['l', 't']
        self.table.add_command(cmd)

        cmd2 = BaseCommand()
        cmd2.name = 'cmd2'
        cmd2.aliases = ['g', 't']
        # This is a duplicate, should raise exception.
        self.assertRaises(DuplicateCommandException, self.table.add_command, cmd2)


class CommandParserTests(DottTestCase):
    def setUp(self):
        self.parser = CommandParser()

    def tearDown(self):
        del self.parser

    def test_simple_command(self):
        """
        Parses a simple command with no args.
        """
        parsed = self.parser.parse('look')
        self.assertIsInstance(parsed, ParsedCommand)
        self.assertEquals(parsed.command_str, 'look')
        self.assertEquals(parsed.arguments, [])
        self.assertEquals(parsed.switches, [])

    def test_command_with_arguments(self):
        """
        Throw some arguments in as well.
        """
        parsed = self.parser.parse('look ship')
        self.assertEquals(parsed.command_str, 'look')
        self.assertEquals(parsed.arguments, ['ship'])
        self.assertEquals(parsed.switches, [])

        parsed = self.parser.parse('look ship hi')
        self.assertEquals(parsed.arguments, ['ship', 'hi'])

    def test_command_with_switches_and_arguments(self):
        """
        The whole she-bang.
        """
        parsed = self.parser.parse('look/quiet ship')
        self.assertEquals(parsed.command_str, 'look')
        self.assertEquals(parsed.arguments, ['ship'])
        self.assertEquals(parsed.switches, ['quiet'])

    def test_poses(self):
        """
        Poses have some shortcuts that are handled differently. Test those
        here, for the MUX/MUSH/MOO folks.
        """
        parsed = self.parser.parse(':taunts you.')
        self.assertEquals(parsed.command_str, 'emote')
        self.assertEquals(parsed.arguments, ['taunts', 'you.'])
        self.assertEquals(parsed.switches, [])

        parsed = self.parser.parse(";'s face is weird.")
        self.assertEquals(parsed.command_str, 'emote')
        self.assertEquals(parsed.arguments, ["'s", 'face', 'is', 'weird.'])
        self.assertEquals(parsed.switches, ['nospace'])