.. _space-building:

.. include:: global.txt

Building in Spaaaacee....
=========================

.. note:: This is all preliminary, and only partially implemented. What
    follows is best described as a scratch pad, that may eventually become
    a space building guide.

Creating Solar Systems
----------------------

Create a solar system:

* @dig/teleport Test Solar System
* @parent here=src.game.parents.space.solar_system.SolarSystemObject

Create two test planets:

* @create Test Planet 1
* @parent Test Planet 1=src.game.parents.space.solar_system.PlanetObject
* @create Test Planet 2
* @parent Test Planet 2=src.game.parents.space.solar_system.PlanetObject

Enter your first test planet so our new ship will be created here:

* enter test planet 1

Create a basic shuttle:

* @create Test Trafficker
* enter Test Trafficker
* @parent here=src.game.parents.space.ships.shuttles.trafficker.TraffickerSpaceShipObject
* @create Cockpit
* enter Cockpit
* @parent here=src.game.parents.space.ships.shuttles.trafficker.TraffickerSpaceShipBridgeObject

You now have a basic space ship. Let's create a Hangar on Test Planet 1:

* @dig/teleport Test Planet 1 Hangar
* @parent here=src.game.parents.space.hangar.RoomHangarObject

Now find the dbref of Test Planet 1 so we can set the hangar's zone. You'll
want to use your dbref in place of ``#36`` below:

* @find Test Planet 1 Hangar
* @zone here=#36

You now have a dockable location. Find your Cockpit object and
teleport to it (use your dbref in place of ``#35`` below):

* @find Cockpit
* @tel #35
* dock

You can now dock at your location like this:

* dock 36

You can also take off like this:

* launch

To warp to the other planet, look at the warp list and warp to it:

* warp
* warp 33