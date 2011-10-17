.. _building:

.. include:: global.txt

Building
========

.. note:: This is all preliminary, and not even partially implemented. What
    follows is best described as a scratch pad, that may eventually become
    a building guide.

Digging Rooms
-------------

* @dig <room-name>

Exits
-----

* @open <alias/dir> <exit-name>[=<dest-dbref>]
@link <exit-dbref>=<dest-dbref>
* @unlink <exit-dbref>

Things
------

@create <thing-name>

Zones
-----

@zone <obj-dbref> = <zone-dbref>

General object commands
-----------------------

* @name <obj-dbref> = <new-name>
* @nuke <dbref>
* @desc <dbref>=<description>

@alias <dbref>=<primary alias> [<alias2>]
@alias/del <dbref>=<alias-to-delete>
@alias/add <dbref>=<alias-to-add>

@parent <dbref>=<parent-class>