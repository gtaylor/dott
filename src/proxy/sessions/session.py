import datetime

from src.utils import logger
from src.server.protocols.proxyamp import SendThroughObjectCmd, TriggerAtSessionDisconnectForObjectCmd, NotifyFirstSessionConnectedOnObjectCmd
from src.proxy.sessions.login_shell import LoginShell

class Session(object):
    """
    This class represents a player's session. Each player gets a session
    assigned to them whenever they connect to the game server. All communication
    between game and player goes through here. 
    """
    def __init__(self, protocol):
        """
        :attr Protocol protocol: Typically
            :class:`src.server.protocols.telnet.MudTelnetProtocol`. This is
            the lower level pipe to and from the user.
        :attr MudService server: The top-level MudService instance found in
            dott.tac.
        :attr tuple address: The user's address and port.
        :attr PlayerAccount account: The account this session is logged in
            as (or None if not logged in.
        """
        # main server properties
        self.protocol = protocol
        self.address = self.protocol.getClientAddress()

        self._mud_service = self.protocol.factory.server

        # This is a reference to a PlayerAccount object, if the user has
        # logged in. If this is None, this session is not logged in.
        self.account = None

        # This is the login shell.
        self.interactive_shell = LoginShell(self)

        # The time the user last issued a command.
        self.cmd_last = datetime.time()
        # Player-visible idle time, excluding the IDLE command.
        self.cmd_last_visible = datetime.time()
        # Total number of commands issued.
        self.cmd_total = 0
        # The time when the user connected.
        self.conn_time = datetime.time()

    def __str__(self):
        """
        String representation of the user session class. We use this a lot in
        the server logs and stuff.
        """
        if self.account:
            symbol = '#'
            username = self.account.username
        else:
            symbol = '?'
            username = None
        return "<%s> %s@%s" % (symbol, username, self.address)

    @property
    def _account_store(self):
        """
        Short-cut to the global account store.

        :rtype: InMemoryAccountStore
        :returns: Reference to the global account store instance.
        """
        return self._mud_service.account_store

    @property
    def _session_manager(self):
        """
        Short-cut to the global session manager.

        :rtype: SessionManager
        :returns: Reference to the global session manager instance.
        """
        return self._mud_service.session_manager
        
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
        self.cmd_last = datetime.time()
        if not idle:
            # Increment the user's command counter.
            self.cmd_total += 1
            # Player-visible idle time, not used in idle timeout calcs.
            self.cmd_last_visible = datetime.time()

    def is_logged_in(self):
        """
        Determines whether this session is a logged in player.

        :rtype: bool
        :returns: ``True`` if this session is logged in, ``False`` otherwise.
        """
        return self.account is not None
        
    def after_session_connect_event(self):
        """
        Triggered right after a connection is established.
        """
        # Shows the login prompt.
        self.interactive_shell.prompt_get_username()

    def after_session_disconnect_event(self):
        """
        Triggered after the protocol breaks connection.
        """
        self._session_manager.remove_session(self)

        if not self.account:
            # This was an unauthenticated user, go no further.
            return

        # Get the object ID that this session was controlling. Do this before
        # session removal to make sure we get a good ID.
        controlled_id = self.account.currently_controlling_id

        # If this session was controlling an object, figure out if this
        # was the last connection active on said object.
        other_sessions = self._session_manager.get_sessions_for_object_id(
            controlled_id
        )

        if not other_sessions:
            # No other session are controlling this object, this was the
            # last to disconnect. Trigger the object's
            # after_session_disconnect_event.
            self._mud_service.proxyamp.callRemote(
                TriggerAtSessionDisconnectForObjectCmd,
                object_id=controlled_id,
            )
    
    def login(self, account):
        """
        After the user has authenticated, this actually logs them in. Attaches
        the Session to the account's default PlayerObject instance.
        """
        # set the session properties 
        self.account = account
        self.conn_time = datetime.time()
        self.interactive_shell = None

        logger.info("Logged in: %s" % self.account.username)

        controlled_id = self.account.currently_controlling_id
        object_sessions = self._session_manager.get_sessions_for_object_id(
            controlled_id)

        if not self._mud_service.is_connected_to_mud_server():
            # Proxy is not connected to MUD server, we can't go any further
            # with events done at time of connection.
            return

        if len(object_sessions) == 1:
            # This is the only Session controlling the object it is associated
            # with. Trigger the 'at connect' event on the object.
            self._mud_service.proxyamp.callRemote(
                NotifyFirstSessionConnectedOnObjectCmd,
                object_id=controlled_id,
            )

        self.execute_command('look')

    def execute_command(self, command_string):
        """
        Used to parse input from a protocol, or something forced.

        :param str command_string: The raw command string to send off to the
            command handler/parser.
        """
        # The time the user last issued a command.
        self.cmd_last = datetime.time()

        if str(command_string).strip().lower() == 'idle':
            # Ignore idle command. This is often used as a keep-alive for
            # people with crappy NATs.
            self.update_counters(idle=True)
            return

        # Player-visible idle time, excluding the IDLE command.
        self.cmd_last_visible = datetime.time()
        # Increment command total
        self.cmd_total += 1

        if self.interactive_shell:
            # Session is "stuck" in an interactive shell. No command parsing
            # happens beyond here, since it's handled by the shell.
            self.interactive_shell.process_input(command_string)
            return

        if self._mud_service.is_connected_to_mud_server():
            # This is the 'normal' case in that we just hand the input
            # off to the command handler.
            self._mud_service.proxyamp.callRemote(
                SendThroughObjectCmd,
                object_id=self.account.currently_controlling_id,
                input=command_string,
            )
        else:
            # proxyamp is a None value, mud server is unavailable.
            self.msg("The MUD server is currently re-loading. Please try "\
                     "your command again in a few seconds.")