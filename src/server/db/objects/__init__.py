from src.server.db.objects.in_memory_store import InMemoryObjectStore

# Go through this object to get/retrieve/query objects. Never go directly
# through CouchDB.
OBJECT_STORE = InMemoryObjectStore()