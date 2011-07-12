from src.utils.test_utils import DottTestCase
from src.server.commands.parser import CommandParser, ParsedCommand

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