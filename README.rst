plone.jsonapi.routes
====================

:Author: Ramon Bartl
:Version: 0.1dev


.. contents:: Table of Contents
   :depth: 2


Introduction
------------

This is an add-on package for plone.jsonapi.core_ which provides some basic
URLs for Plone standard contents.


Installation
------------

There is currently no "official" release on pypi, so you have to use
`mr.developer` to include plone.jsonapi.routes_ to your buildout config.

Example::

    [buildout]

    extensions =
        mr.developer

    auto-checkout = *

    [sources]
    plone.jsonapi.core   = git https://github.com/ramonski/plone.jsonapi.core.git branch=develop
    plone.jsonapi.routes = git https://github.com/ramonski/plone.jsonapi.routes.git branch=develop

    [instance]
    ...
    eggs =
        ...
        plone.jsonapi.core
        plone.jsonapi.routes


License
-------

MIT - do what you want


.. _Plone: http://plone.org
.. _Dexterity: https://pypi.python.org/pypi/plone.dexterity
.. _Werkzeug: http://werkzeug.pocoo.org
.. _plone.jsonapi.core: https://github.com/ramonski/plone.jsonapi.core
.. _plone.jsonapi.routes: https://github.com/ramonski/plone.jsonapi.routes
.. _mr.developer: https://pypi.python.org/pypi/mr.developer
.. _Utility: http://developer.plone.org/components/utilities.html

.. vim: set ft=rst ts=4 sw=4 expandtab :
