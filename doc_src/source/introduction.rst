.. _introduction:

.. include:: global.txt

Introduction
============

Dawn of the Titans (dott) is a MUD server that I (gtaylor_) am working on for
the space-themed game I've been kicking around in my head for a long time.
It is very much a "work on it when I feel like it" project, any may never
fully come to fruition as a running game.

The text-based medium is still special for me, and I think using projects
such as these in order to learn new things and hone existing skills is great.
Scratching multiple itches with one... stick?

Under the hood
--------------

dott is powered by Python_, and is built on the excellent Twisted_ framework.
CouchDB_ is used for data storage, but the game itself is entirely memory
resident (so we're not really using any of CouchDB_'s unique capabilities).

Nifty features
--------------

* A two-process proxy and MUD server architecture that allows connections to
  be maintained while the MUD server is down or rebooting.
* An extremely simple JSON DB structure (CouchDB_ speaks JSON).
* The great async capabilities that Twisted_ brings to the table.

Where to go for getting help, reporting bugs, and sharing ideas
---------------------------------------------------------------

.. warning:: Before going into any further detail, it is important to note
    that this codebase exists for the very selfish purpose of running a single,
    specific game on it. I (gtaylor_) am not writing this as a general-purpose
    codebase. I am solely focused on my eventual game, so please do not take
    it personally if I am not interested in your idea! But please do fork
    away and make it your own.

The best way to get help, report bugs, or share ideas is our `issue tracker`_.
We make a conscious effort to watch and respond to things there.

License
-------

dott is covered under the extremely permissive `BSD License`_. Just please
leave the copyright and attribution notices be and I'll be happy.