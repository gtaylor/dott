from src.server.config.in_memory_store import InMemoryConfigStore

# Go through this object to get/retrieve config values. Never go directly
# through CouchDB.
CONFIG_STORE = InMemoryConfigStore()