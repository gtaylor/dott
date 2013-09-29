#!/bin/bash
/usr/bin/pg_dump --host 162.243.2.209 --port 5432 --username "dott" --format plain --schema-only --no-privileges --verbose --file "/home/gtaylor/workspace/dott/misc/dott-schema.sql" "dott"
