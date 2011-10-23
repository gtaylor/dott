.. _scribbles:

.. include:: global.txt

Scribbles
=========

This is a random assortment of various scribbles. Concepts graduate
from here, moving into their own relevant documents over time.

Universe Arrangement
--------------------

The universe can be of any general shape, with the new player starting area
in the center. The inner core of the universe will be safe, in that you
can't attack other players in it. As one moves further outward, it becomes
open season for everyone.

System Security
---------------

For now, we'll just have 'law-less' and 'policed' security states. In
law-less systems, anyone can shoot anyone. In 'policed' systems, you can
only shoot NPCs.

Mining
------

Make this more fun than EVE and other games. Mining will be done by firing
oneself or remote-controlled robots at an asteroid. The player then works
through a randomly generated area, finding ores and potentially fighting
weird life forms.

Issues to work through:

* If the player is remote-controlling a robot, need some way to alert the
  player of things going on with their ship. IE: Someone warps in, or someone
  starts firing on them.
* Facilities for taking control of objects needs to be absolutely stout.
  Make sure to handle damage to their dormant player object.

Manufacturing
-------------

This can probably be a little more 'boring', at least initially. Assembly
lines can be rented or installed in larger ships or bases. I like EVE's
blueprint system for this. BPOs, BPCs. Make these relatively easy to obtain.
BPOs for all of the common stuff. BPCs for everything else.

Ship stuff
----------

Each system is like an area. Points within the system are like rooms
(near a warp gate, orbiting a planet, in an asteroid field, etc). Players
move around the system by warping. They may interact with any other ship
in their current location.

Traveling between systems is done by jumping through warp gates.

Warping
^^^^^^^

Warping should put the player's ship in a "warping" state, where they can't
be messed with, but still show up on long range scanners.

Ship info
^^^^^^^^^

status (Ship status display)
modules/mods (Ship module display)
weaps/weapons (Weapon display)

Movement
^^^^^^^^

land or dock (Lists all landable/dockable places)
land <dest> or dock <dest> (Lands/docks somewhere)
warp (Lists all warp points)
warp <dest> (Warps to a point in the system. Gates, planets, etc.)
jump <gate> (Jumps through a warp gate or wormhole.)

Combat
^^^^^^

fire 1 <target> (Fires first weapon at target)
  f 1 <target>
fire <target> (Fires all weapons at target)
  f <target>
fire - (stops all weapons)
  f -
fire stop (stops all weapons)
  f s
stop 1 (Stops firing weapon)
  s 1
stop (stops all weapons)
  s
activate 1 (Activates add-on module 1)
  a 1
deactivate 1 (Deactivates add-on-module 1)
  d 1
activate all (Activates all add-on modules)
  a all
deactivate all (De-activates all add-on modules)
  d all