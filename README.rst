Mines DirSearch Python Library, CLI, and Mutt Integration
=========================================================

The `Mines DirSearch`_ website allows search of Mines personnel who have their
directory information listed in the Banner system. This is a convenient Python
interface to that website.

.. _`Mines DirSearch`: https://webapps.mines.edu/DirSearch

:Author: Jack Rosenthal
:Requires: Python 3.4 or greater, Beautiful Soup 4.4.0 or greater, Requests
:License: MIT
:Contributing: See ``CONTRIBUTING.rst``.

Installing
----------

Clone `the repository`_ and install::

    $ pip install . --user

Or install from PyPI::

    $ pip install csmdirsearch --user

.. _`the repository`: https://github.com/jackrosenthal/csmdirsearch

Usage from Python
-----------------

Use ``search(query)`` to search for a user by either (part of) a username, or
(part of) a full name. ``search`` is a generator that will yield unique
``Person`` objects. Typical attributes on this object include ``name``,
``business_email``, ``major``, ``classification``, and ``department``; however,
only the ``name`` attribute is guaranteed to exist.

Each ``Person`` object also has a few properties:

:``username``:
    Based on the ``business_email`` (and potentially more information in the
    future), a "best guess" for the username of the user, otherwise ``None``.
:``desc``:
    An automatic, brief description of the person, for example:
    ``Undergraduate Student, Computer Science``.

The ``name`` of each person is also a special ``Name`` type, containing
``first``, ``last``, and ``nick`` attributes. You can convert a name to a
string using the ``strfname`` function, or use ``str(person.name)`` for a
"reasonable default":

>>> name = Name("Rosenthal, Jack (NickName)")
>>> name.strfname("{first} {last}")
'Jack Rosenthal'
>>> str(name)
'Jack (NickName) Rosenthal'

There's also convenience properties to be used in ``strfname``:

:``pfirst``:
    Short for "preferred first". This will be set to ``nick`` if there is a
    nick name, ``first`` otherwise.
:``nickp``:
    Short for "nick, wrapped in parens, if there is one". This will be set to
    ``' (nick)'`` if there's a nick name, ``''`` otherwise.

Example:

>>> name = Name("Rosenthal, Jack (NickName)")
>>> name.strfname("{pfirst} {last}")
'NickName Rosenthal'
>>> name.strfname("{first}{nickp} {last}")
'Jack (NickName) Rosenthal'

Here is an example::

    import csmdirsearch
    for person in csmdirsearch.search("Jack Rosenthal"):
        print(person.name, person.desc)

If you wish to limit your search to **just** a partial username (no real
names), use the ``search_by_partial`` generator instead of ``search``.

Finally, if you wish to limit your search to **just** a partial full name (most
efficent), use the ``search_by_name`` generator instead of ``search``. This
generator also has means to limit a search to a certain classification or
department. Read the source code for more details.

Usage from the Command Line
---------------------------

This is wicked simple::

    $ dirsearch "Jack Rosenthal"
    Jack Rosenthal
    Undergraduate Student
    Business Email: ...

If you wish to use the ``search_by_name`` or ``search_by_partial`` functions to
limit the scope of the input, use ``--input=name`` or ``--input=partial``
respectively::

    $ dirsearch --input=partial "jrosent"
    Jack Rosenthal
    ...

Usage from Mutt
---------------

Add to your ``.muttrc``::

    set query_command = "dirsearch --format=mutt %s"

Then press ``Q`` to compose using a search, or ``^T`` while writing a name or
address.

