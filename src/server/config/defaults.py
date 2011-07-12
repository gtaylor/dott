"""
Default config values. If no value for a config parameter can be found
in the config DB in in_memory_store, these values are pulled as defaults.
"""
DEFAULTS = {
    # TODO: Implement this.
    'IDLE_TIMEOUT': 3600,
    # This will be set at initial DB creation.
    'NEW_PLAYER_ROOM': None,
}