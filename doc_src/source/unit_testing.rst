.. _unit_testing:

.. include:: global.txt

Running Unit Tests
==================

Unit tests are the preferred means of developing new features, and testing
existing functionality for regressions. While we do have and do accept some
changes without unit tests, we strongly prefer them.

If you look around the ``dott`` directory structure, you will see files named
in the pattern of :file:`tests.py`. These contain unit tests. They are
scattered around the codebase with the code that they test. For example,
in :file:`src/server/objects/`, you'll see a :file:`in_memory_store.py`
module, and the unit tests for it at :file:`tests.py`.

Before you begin
----------------

Unit tests are ran via ``nose``, which is a unit testing module. You can
install that like this::

    easy_install nose

Or if you have pip::

    pip install nose

Running all unit tests
----------------------

To run the entire suite, first make sure that you are in the top-level
:file:`dott` directory. Then do this::

     PYTHONPATH=. nosetests -s

.. note:: This will run the entire unit test suite. The -s captures stdout
    output, which is needed to show ``print`` statements, if you're using them
    while developing (they shouldn't be in your final commit/pull request).

Getting more specific with test selection
-----------------------------------------

If you'd only like to run a certain test module, simply provide its name::

     PYTHONPATH=. nosetests -s src/server/objects/tests.py

Since tests are grouped by :class:`TestCase` classes, each of these modules will
probably contain a handful of different :class:`TestCase` sub-classes for the
various API calls. For example, the
:file:`src/server/objects/tests.py` module
has :class:`InMemoryObjectStoreTests`. Let's say we
only want to run the tests in :class:`InMemoryObjectStoreTests`::

     PYTHONPATH=. nosetests -s src/server/objects/tests.py:InMemoryObjectStoreTests

Now we're narrowed down to just the :class:`InMemoryObjectStoreTests` TestCase
object. But what if we just want to run one of the unit test methods on that
class? For example, the :py:meth:`test_create_room` method::

     PYTHONPATH=. nosetests -s src/server/objects/tests.py:InMemoryObjectStoreTests.test_create_room

We're now only running that specific unit test. This is useful when
developing methods, or tracking a specific regression.
