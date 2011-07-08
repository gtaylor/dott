from src.server.accounts.db_store import DBAccountStore

# Go through this object to get/retrieve accounts values. Never go directly
# through CouchDB.
ACCOUNT_STORE = DBAccountStore()