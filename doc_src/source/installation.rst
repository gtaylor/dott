.. _installation:

.. include:: global.txt

Installing dott
===============

Setting up virtualenv + virtualenvwrapper
-----------------------------------------

You'll want to install all of your pre-reqs in a virtual environment. This
keeps a clone of your Python interpreter sandboxed elsewhere, allowing you
to install specific versions of support packages that might be different
from those found in your system's global Python install.

Install and set up the following two utilities for doing this:

* virtualenv_ (Shouldn't really require any setup)
* virtualenvwrapper_ (Requires some manual work, no Windows support)

Create your virtualenv::

    mkdir ~/.virtualenvs
    mkvirtualenv dott

Install prereqs
---------------

Install pip in your newly created ``dott`` virtualenv, and have it install
everything in the :file:`requirements.txt` file::

    easy_install pip
    pip install -r requirements.txt

You'll also need to install CouchDB_. The instructions to do so vary, but
most Linux distributions have this packaged already. Once you have CouchDB_
set up, Futon_ is pretty helpful for browsing/editing the contents of your
various DBs (they'll be created at the game's first boot).

Clone the repository
--------------------

Your environment is ready, time to get a copy of the code (if you haven't
already). You'll want to pull either from the main gtaylor/dott repository,
or your own fork (if you've forked the project)::

    git clone git://github.com/gtaylor/dott.git

Amazon Simple Email Service
---------------------------

dott does not use a traditional SMTP connection. It'd be possible to write
an SMTP backend, and we'd welcome the contribution for our developers, but
I (gtaylor) don't want to spend the time on it myself.

You'll need an `Amazon AWS`_ account, and you'll need to sign up for SES_.
Signup is free, and I'll be shocked if you manage to even ring up a few
pennies worth of usage. Sign up for both of these, and get your AWS API keys.
You'll need them for the next step.

Once you're signed up, copy/paste the following into a Python module then
run it::

    import boto

    # Substitute these two values with your own.
    conn = boto.connect_ses('ACCESS_KEY', 'SECRET_KEY')
    # A verification email will be sent to whatever address you want to send
    # as, so you'll need to be able to check the inbox.
    conn.verify_email_address('your.email@somewhere.com')

Once you receive the verification email for whatever address you state that
you'll be sending as, follow the link in the email and that specific address
will be verified as a valid "Send As" value for SES_.

Configuration
-------------

:command:`cd` into the newly created :file:`dott` directory, and take a look
at :file:`settings.py`. You don't want to change any of the values in there.
Instead, create a new file called :file:`local_settings.py` and copy/paste
the setting you'd like to override into said new file.

You'll need to change the following values at minimum:

* ``SECRET_KEY`` (used for hashing account passwords)
* ``AWS_ACCESS_KEY_ID`` (get this from your AWS account web dashboard)
* ``AWS_SECRET_ACCESS_KEY`` (get this from your AWS account web dashboard)
* ``SERVER_EMAIL_FROM`` (must be the email address you verified with SES_)

Starting the game
-----------------

dott is split into two different processes:

* Telnet proxy (:file:`proxy.tac`)
* MUD Server (:file:`server.tac`)

The proxy server accepts telnet connections and handles user authentication
and registration. It deals with all of the boring protocol-related stuff to
get players connected and whatnot. It also maintains everyone's connection if
the MUD server goes down, allowing for seamless reboots without most players
ever noticing.

The MUD server handles all of the game-related stuff. It holds the world,
tracks NPCs, handles combat, and does all of the fun stuff. The proxy just
pipes input into the MUD server, and spits back out whatever the MUD server
says.

You'll need to start the two pieces separately::

    twistd --pidfile=proxy.pid -ny proxy.tac
    twistd --pidfile=server.pid -ny server.tac

After you run both of these, you should be able to connect to port 4000 and
create a character.

.. note:: You may stop/start the two processes independently of one another,
    and normal operation will resume once they are both running at the same
    time. It's perfectly acceptable to restart server.tac, and is in fact
    how we handle code reloading.