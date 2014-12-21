Installation
============

This package depends on two external libraries, `plone.jsonapi.core`_ and
`plone.api`_. The first one is the core framework which takes care of the
dispatching of requests and route registration. The latter one is a simplified
API to the Plone_ CMS.


Buildout
--------

The simplest way to install plone.jsonapi.routes is to add it to the buildout
configuration::

    [buildout]

    ...

    [instance]
    ...
    eggs =
        ...
        plone.jsonapi.routes


Run the buildout and your Plone site will become RESTful_.

The routes for the standard Plone_ content types get registered on startup.
The following URL should be available after startup:

http://localhost:8080/Plone/@@API/plone/api/1.0


JSONView
--------

Use the JSONView Plugin for your browser to view the generated JSON in a more
comfortable way. You can find the extensions here:

- Firefox: https://addons.mozilla.org/de/firefox/addon/jsonview

- Chrome: https://chrome.google.com/webstore/detail/jsonview/chklaanhfefbnpoihckbnefhakgolnmc?hl=en


Advanced Rest Client
--------------------

Use this Chrome Plugin to send POST request to the Plone JSON API. You can
find it here:

https://chrome.google.com/webstore/detail/advanced-rest-client/hgmloofddffdnphfgcellkdfbfbjeloo


.. Links

.. _plone.jsonapi.core: https://pypi.python.org/pypi/plone.jsonapi.core
.. _plone.jsonapi.routes: https://pypi.python.org/pypi/plone.jsonapi.routes
.. _plone.api: https://pypi.python.org/pypi/plone.api
.. _Plone: http://plone.org
.. _RESTful: http://en.wikipedia.org/wiki/Representational_state_transfer

.. vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
