import time

from src.utils import logger
from src.game.commands.shells.login import LoginShell

class Session(object):
    """
    This class represents a player's session. Each player
    gets a session assigned to them whenever
    they connect to the game server. All communication
    between game and player goes through here. 
    """
    def __init__(self, protocol):
        """
        This sets up the main parameters of
        the session. The game will poll these
        properties to check the status of the
        connection and to be able to contact
        the connected player. 
        """
        # main server properties
        self.protocol = protocol 
        self.server = self.protocol.factory.server
        self.address = self.protocol.getClientAddress()

        # player setup 
        self.name = None
        self.uid = None
        self.logged_in = False

        # This is the login shell.
        self.interactive_shell = LoginShell(self)

        # The time the user last issued a command.
        self.cmd_last = time.time()
        # Player-visible idle time, excluding the IDLE command.
        self.cmd_last_visible = time.time()
        # Total number of commands issued.
        self.cmd_total = 0
        # The time when the user connected.
        self.conn_time = time.time()

    def __str__(self):
        """
        String representation of the user session class. We use
        this a lot in the server logs and stuff.
        """
        if self.logged_in:
            symbol = '#'
        else:
            symbol = '?'
        return "<%s> %s@%s" % (symbol, self.name, self.address)
        
    def msg(self, message):
        """
        Sends a message to the player.
        """
        self.protocol.msg(message)

    def disconnect_client(self):
        """
        Disconnects the user.
        """
        self.protocol.disconnectClient()
      
    def update_counters(self, idle=False):
        """
        Hit this when the user enters a command in order to update idle timers
        and command counters.

        :keyword bool idle: When ``True``, the public-facing idle time is
            not updated.
        """
        # Store the timestamp of the user's last command.
        self.cmd_last = time.time()
        if not idle:
            # Increment the user's command counter.
            self.cmd_total += 1
            # Player-visible idle time, not used in idle timeout calcs.
            self.cmd_last_visible = time.time()
        
    def show_game_connect_screen(self):
        """
        Show the banner screen. Grab from the 'connect_screen'
        config directive. If more than one connect screen is
        defined in the ConnectScreen attribute, it will be
        random which screen is used. 
        """
        self.interactive_shell.prompt_ask_username()
    
    def login(self, player):
        """
        After the user has authenticated, this actually
        logs them in. At this point the session has
        a User account tied to it. User is an django
        object that handles stuff like permissions and
        access, it has no visible precense in the game.
        This User object is in turn tied to a game
        Object, which represents whatever existence
        the player has in the game world. This is the
        'character' referred to in this module. 
        """
        # set the session properties 

        user = player.user
        self.uid = user.id
        self.name = user.username
        self.logged_in = True
        self.conn_time = time.time()
        self.interactive_shell = None
        
        logger.info("Logged in: %s" % self)

    def execute_command(self, command_string):
        """
        Used to parse input from a protocol, or something forced.

        :param str command_string: The raw command string to send off to the
            command handler/parser.
        """
        if str(command_string).strip().lower() == 'idle':
            # Ignore idle command. This is often used as a keep-alive for
            # people with crappy NATs.
            self.update_counters(idle=True)
            return

        if self.interactive_shell:
            self.interactive_shell.process_input(command_string)
        