.. _ships-basic_operation:

====================
Basic ship operation
====================

Assumptions
-----------

This guide assumes that the reader either has a ship, or is interested in
learning more about how ships work before purchasing one. We assume that the
reader's ship is landed in some hangar (whether it be on a planet, in a station,
or inside of another ship).

Entering a landed ship
----------------------

Before following any of the instructions in this guide, you'll want to enter
your ship. You can do so using the :command:`enter` command from within a
hangar.

Depending on the size of the ship you are entering, you will either hop
straight into the cockpit, or find yourself in one of the ship's rooms (probably
the airlock). Fighters and some Frigates are small enough to only have a
single "section", the cockpit. Larger ships have multiple sections/rooms
within, so you'll need to find the *Bridge*. A ship's Bridge is functionally
equivalent to a smaller ship's Cockpit, it's just much bigger and can hold
quite a few people.

.. tip:: The only place a ship may be controlled from is its Cockpit or Bridge.

Inspecting your ship
--------------------

The best overall indicator of your ship's status and general health can be
found via the :command:`status` command. This will show you a quick, high
level view of things such as:

* Where your ship is.
* Armor and Shield levels.
* Any special conditions being applied to the ship (jammed,
  warp scrambled, etc.)
* A very brief weapons/module readout.

.. warning:: Show some example command output here.

You'll want to consult your status readout during combat to help keep track
of how you're holding up.

Taking off
----------

Your ship should be sitting in a hangar of some sort at this point. To take
off and get into space, you'll want to use the :command:`launch` command.

After a short delay, you'll find your ship floating out in space by whatever
planet/station/ship you launched from.

.. note:: Many ship commands aren't available while landed/docked.

Looking at your surroundings
----------------------------

Whether you are in a single-seat Fighter or a massive Carrier, your only
reliable view of the outside world comes courtesy of your ship's sensors.
To see what other ships or objects are near your ship, you'll use the
:command:`contacts` command. Only ships that are in the same location as you
will be shown with this readout.

.. warning:: Show some example command output here.

Some basic details on what each object is are returned, along with its unique
numerical ID. You will use this numerical ID with any command that interacts
with objects in space.

Scanning ships/objects in space
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To get more details on something that neighbors you in space, use the
:command:`scan` command with the ship/object's unique ID number. For example,
if a Fighter in your location has the ID ``1835``, I could scan it like this::

    scan 1835

This will return a readout very similar to your own ``status`` command. The big
difference is that some of the information will be less specific, or omitted
altogether.

.. note:: Any time you scan another ship, its sensors may notice. This
    depends on your scanner and your target's sensors. Know that some pilots
    take scanning as an aggressive action.

