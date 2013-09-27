#!/bin/bash
/usr/bin/pg_dump --host localhost --port 5432 --username "postgres" --no-password  --format plain --section pre-data --section data --section post-data --inserts --no-privileges --verbose --file "/home/gtaylor/workspace/dott/misc/dott-schema.sql" "dott"
