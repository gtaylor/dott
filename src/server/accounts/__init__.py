from src.server.accounts.in_memory_store import InMemoryAccountStore

# Go through this object to get/retrieve accounts values. Never go directly
# through CouchDB.
ACCOUNT_STORE = InMemoryAccountStore()