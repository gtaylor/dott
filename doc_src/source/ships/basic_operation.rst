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

.. note:: Entry to ships is restricted based on identity and/or corporate
    affiliation. Make sure you're entering your own ship.

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

Launching from a Hangar
-----------------------

Your ship should be sitting in a hangar of some sort at this point. To take
off and get into space, you'll want to use the :command:`launch` command.

After a short delay, you'll find your ship floating out in space by whatever
planet/station/ship you launched from.

.. note:: Many ship commands aren't available while landed/docked.

Sensors and Scanners
--------------------

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

Navigating Solar Systems
------------------------

Your ship should now be outside of whatever planet/station/ship it launched
from. You are now flying around in a *Solar System*. You can see which
Solar System you're in via the :command:`status` command. Solar Systems
are inter-connected by *Jump Gates*, which we'll cover in more detail later.

Solar Systems are partitioned into *Locations*. For example, "Near Station J12",
"Near the Sol Jump Gate", or "In Asteroid Belt 12". These are roughly equivalent
to a traditional MUD's Rooms. If Location is to Room, Solar System is to a
traditional MUD's Areas or Zones.

Ships can only interact with other ships that are in the same location. For
example, it's not possible to fire at a ship that is near the "Sol Jump Gate"
from your position in "Asteroid Belt 12".

Warping to Locations
^^^^^^^^^^^^^^^^^^^^

Almost every ship in the game is equipped with a Faster-Than-Light warp drive.
These drives are the way you get from Location to Location within a
Solar System. To see your current location, you use the :command:`status`, or
the :command:`warp` command with no arguments.

To see a full list of locations that you may warp to, use the :command:`warp`
command with no arguments.

.. warning:: Show some example command output here.

Note that each Location has a unique ID number, just like ships do. You'll
use this number with the :command:`warp` command to warp around the system.
For example, let's say we have a Location called "Asteroid Belt 12" that
has a unique identifier of ``1832``::

    warp 1832

This would fire up our warp drive, and after a brief delay, we'd appear in
the Asteroid Belt.

Traveling to Different Systems
------------------------------

To travel to different systems, you'll first need to :command:`warp` to a
*Jump Gate*. Jump Gates are large, stationary mass accelerators that fling you
to distant locations.

Once you have picked out and warped to a Jump Gate, you'll actually jump through
it with the :command:`jump` command. Note that it is not necessary to specify
any arguments with the :command:`jump` command, as we can infer that you moved
to a specific Jump Gate by warping there.

After a short delay, you will find yourself far from where you started. You
are then free to :command:`warp` around your new Solar System, or
:command:`jump` back to your previous location.

Docking/Landing
---------------

It is very unwise to leave your ship floating out in space when you retire
for the night. It is unlikely that your neighbors will resist the temptation
to destroy your ship (with your character in it).

You may dock or land your ship on Planets, Stations, or other Ships. Your
options will vary based on who you are, your corporate affiliation, and your
personal and corporate standings.

The easiest way to find likely places to dock is to look at your
:command:`warp` list for Locations that look like Planets or Stations. Warp
to either of these, then use the :command:`dock` command with no arguments
to see a list of docking/landing options for your current Location. Like
almost everything else, each location has a unique ID, which you can use
with the :command:`dock` command::

    dock 1293

After a short delay, your ship ends up in whatever hangar you selected.

.. note:: Your docking options may vary based on your identity and
    corporate affiliation.
