#!/bin/bash
PYTHONPATH=. trial \
	src.accounts.tests \
	src.game.parents.base_objects.tests \
	src.daemons.server.commands.tests \
	src.daemons.server.objects.tests \
	src.daemons.server.objects.parent_loader.tests

