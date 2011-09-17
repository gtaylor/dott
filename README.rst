==================
Dawn of the Titans
==================

:Info: A space-themed MUD server
:Author: Gregory Taylor

An overview
===========
Dawn of the Titans is a Twisted Python based MUD server that I work on in my
limited free time. Progress is slow and erratic, and this project may or may not
ever evolve into something live.

This codebase draws heavily what I learned while developing Evennia_. If you
are looking at starting a game that doesn't fit my feature set, you're going
to be much better served by developing on Evennia_. DotT is meant for a very
specific purpose (my individual game), and is not a one-size-fits-all
package like Evennia_.

.. _Evennia: http://evennia.com

The general idea
================

The general idea and goal of this project is to combine desirable elements from
several of my favorite sci-fi games:

* EVE Online
* Battletech
* Tradewars

The space system will feel very much like text-based EVE online, some of the
combat rules and units will feel Battletechy, and the econ and planetary
interactions may borrow from Tradewars.

In addition to a simple but interesting space system, we'd also like to
eventually beef up meatspace (IE: things done outside and within ships,
aside from controlling ships). Boarding parties, docking on stations,
landing on planets, and all other sorts of things are possible.

.. note:: We probably won't even get a quarter of these implemented, but
   dream big, right?

Status, contributing, and my self-serving greed
===============================================

DotT is under perpetual unstable development. This is a hobby project, and
there are no guarantees of backwards compatibility at any time. I am not
extremely interested in spending time on anything but what my eventual game
may need, so if you want/need something, you very well may be on your own.

That said, post an issue and I'll let you know if we have mutual desires.
Pull requests will be considered with an open mind (as long as they
don't disrupt the standard feature set and include unit tests).

Documentation
=============

Read the documentation_ for more details on installation, development,
and etc.

.. _documentation: http://dott.rtfd.org/

License
=======

The project is licensed under the `BSD License`_.

.. _BSD License: https://github.com/gtaylor/dott/blob/master/LICENSE
