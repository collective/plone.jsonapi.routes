plone.jsonapi.routes
====================

:Author: Ramon Bartl
:Version: 0.3


.. contents:: Table of Contents
   :depth: 2


Introduction
------------

This is an add-on package for plone.jsonapi.core_ which provides some basic
URLs for Plone standard contents (and more).


Motivation
----------

The routes package is built on top of the plone.jsonapi.core_ package to allow
Plone developers to build modern (JavaScript) web UIs which communicate through
a RESTful_ API with their Plone site.


Compatibility
-------------

The plone.jsonapi.routes_ is compatible with Plone_ 4.


Installation
------------

The official release is on pypi_, so you have to simply include
plone.jsonapi.routes_ to your buildout config.

Example::

    [buildout]

    ...

    [instance]
    ...
    eggs =
        ...
        plone.jsonapi.core
        plone.jsonapi.routes


The routes for the standard Plone_ content types get registered on startup.

The following URL should be available after startup:

http://localhost:8080/Plone/@@API/plone/api/1.0


API URL
-------

After installation, the Plone API routes are available below the
plone.jsonapi.core_ root URL (`@@API`) with the base ``/plone/api/1.0``, for example
``http://localhost:8080/Plone/@@API/plone/api/1.0/api.json``.

.. note:: Please see the documentation of plone.jsonapi.core_ for the API root URL.


There is also an overview of the registered routes which can be accessed here:

http://localhost:8080/Plone/@@API/plone/api/1.0/api.json


API Routes
----------

:BASE_URL: `/plone/api/1.0`

This is an overview of the provided API Routes. The basic content routes
provide **all** an interface for CRUD_ operations.

CRUD_ URL Scheme:

+-----------+---------------------------------------------+--------+
| OPERATION | URL                                         | METHOD |
+===========+=============================================+========+
| VIEW      | <BASE_URL>/<RESOURCE>/<uid:optional>        | GET    |
+-----------+---------------------------------------------+--------+
| CREATE    | <BASE_URL>/<RESOURCE>/create/<uid:optional> | POST   |
+-----------+---------------------------------------------+--------+
| UPDATE    | <BASE_URL>/<RESOURCE>/update/<uid:optional> | POST   |
+-----------+---------------------------------------------+--------+
| DELETE    | <BASE_URL>/<RESOURCE>/delete/<uid:optional> | POST   |
+-----------+---------------------------------------------+--------+

.. important:: the optional UID of the create, update and delete URLs is to
               specify the target container where to create the content.  If
               this is omitted, the API expects a parameter `parent_uid` in the
               request body JSON. If this is also not found, an API Error will
               be returned.


Request Parameters
------------------

All `GET` resources acceppt request parameters.

+------------+----------+------------------------------------------------------------+
| Parameter  | Type     | Description                                                |
+============+==========+============================================================+
| limit      | number   | limit the search results                                   |
+------------+----------+------------------------------------------------------------+
| sort_on    | index    | sort the results by the given catalog index                |
+------------+----------+------------------------------------------------------------+
| sort_order | asc/desc | sort ascending/descending                                  |
+------------+----------+------------------------------------------------------------+
| q          | query    | search the SearchableText index for the given query string |
+------------+----------+------------------------------------------------------------+
| creator    | username | search for items which were created by the given user      |
+------------+----------+------------------------------------------------------------+

Examples
~~~~~~~~

- Search for documents and return 10 results

  http://localhost:8080/Plone/@@API/plone/api/1.0/documents?limit=10

- Search all content created by admin

  http://localhost:8080/Plone/@@API/plone/api/1.0/documents?creator=admin

- Search for documents which contain the text `Open-Source`

  http://localhost:8080/Plone/@@API/plone/api/1.0/documents?q=Open-Source

- Search for all documents created by admin which contain the text `Open-Source`

  http://localhost:8080/Plone/@@API/plone/api/1.0/documents?q=Open-Source&creator=admin


Response Format
---------------

The response format is for all resources the same.

Example::

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents",
        count: 0,
        _runtime: 0.0021538734436035156,
        items: [ ]
    }

**url**
    The resource root url
**count**
    Count of found results
**_runtime**
    The processing time in milliseconds after the request was received until
    the respone was prepared.
**items**
    An array of result items


Content URLs
------------

:BASE_URL: `/plone/api/1.0`
:SCHEME:   `BASE_URL/RESOURCE`

All content informations are dynamically gathered by the contents schema
definition through the `IInfo` adapter.  It is possible to define a more
specific adapter for your content type to control the data returned by the API.

+-------------+--------------------------------------------------+
| Resource    | Description                                      |
+=============+==================================================+
| folders     | Resource for all Folder contents                 |
+-------------+--------------------------------------------------+
| documents   | Resource for all Page contents                   |
+-------------+--------------------------------------------------+
| events      | Resource for all Event contents                  |
+-------------+--------------------------------------------------+
| files       | Resource for all File contents                   |
+-------------+--------------------------------------------------+
| images      | Resource for all Image contents                  |
+-------------+--------------------------------------------------+
| links       | Resource for all Link contents                   |
+-------------+--------------------------------------------------+
| newsitems   | Resource for all News Item contents              |
+-------------+--------------------------------------------------+
| topics      | Resource for all Collection (old style) contents |
+-------------+--------------------------------------------------+
| collections | Resource for all Collection contents             |
+-------------+--------------------------------------------------+


Special URLs
------------

:BASE_URL: `/plone/api/1.0`
:SCHEME:   `BASE_URL/RESOURCE`

Beside the content URLs described above, there are some other resources
available in this extension.

+---------------+--------------------------------+
| Resource      | Description                    |
+===============+================================+
| users         | Resourece for all Plone Users  |
+---------------+--------------------------------+
| users/current | Get the current logged in user |
+---------------+--------------------------------+


Write your own API
------------------

This package is designed to provide an easy way for you to write your own JSON
API for your custom Dexterity_ content types.

The plone.jsonapi.example_ package shows how to do so.


Example
~~~~~~~

Lets say you want to provide a simple CRUD_ JSON API for your custom Dexterity_
content type. You want to access the API directly from the plone.jsonapi.core_
root URL (`http://localhost:8080/Plone/@@API/`).

First of all, you need to import the CRUD_ functions of plone.jsonapi.routes_::

    from plone.jsonapi.routes.api import get_items
    from plone.jsonapi.routes.api import create_items
    from plone.jsonapi.routes.api import update_items
    from plone.jsonapi.routes.api import delete_items

To register your custom routes, you need to import the `router` module of
plone.jsonapi.core_. The `add_route` decorator of this module will register
your function with the api framework::

    from plone.jsonapi.core import router

The next step is to provide the a function which get called by the
plone.jsonapi.core_ framework::

    @router.add_route("/example", "example", methods=["GET"])
    def get(context, request):
        return {}

Lets go through this step by step...

The `@router.add_route(...)` registers the decorated function with the framework.
So the function will be invoked when someone sends a request to `@@API/example`.

The framework registers the decorated function with the key `example`.
We also provide the HTTP Method `GET` which tells the framework that we only
want to get invoked on a HTTP GET request.

When the function gets invoked, the framework provides a context and a request.
The context is usually the Plone_ site root, because this is where the base
view (`@@API`) is registered. The request contains all needed parameters and
headers from the original request.

At the moment we return an empty dictionary. Lets provide something more useful here::

    @router.add_route("/example", "example", methods=["GET"])
    def get(context, request=None):
        items = get_items("my.custom.type", request, uid=None, endpoint="example")
        return {
            "count": len(items),
            "items": items,
        }

The `get_items` function of the `plone.jsonapi.routes.api` module does all the
heavy lifting here. It searches the catalog for `my.custom.type` contents,
parses the request for any additional parameters or returns all informations of
the "waked up" object if the `uid` is given.

The return value is a list of dictionaries, where each dictionary represents
the information of one result, be it a catalog result or the full information
set of an object.

.. note:: without the uid given, only catalog brains are returned

Now we need a way to handle the uid with this function. Therefore we can simple
add another `add_route` decorator around this function::

    @router.add_route("/example", "example", methods=["GET"])
    @router.add_route("/example/<string:uid>", "example", methods=["GET"])
    def get(context, request=None, uid=None):
        return get_batched("my.custom.type", request, uid=uid, endpoint="example")

This function handles now URLs like `@@API/example/4b7a1f...` as well and
invokes the function directly with the provided UID as the parameter. The
`get_items` tries to find the object with the given UID to provide all
informations of the waked up object.

.. note:: API URLs which contain the UID are automatically generated with the provided endpoint


The `CREATE`, `UPDATE` and `DELETE` functionality is basically identical with
the basic `VIEW` function above, so here in short::

    # CREATE
    @router.add_route("/example/create", "example_create", methods=["POST"])
    @router.add_route("/example/create/<string:uid>", "example_create", methods=["POST"])
    def create(context, request, uid=None):
        items = create_items("plone.example.todo", request, uid=uid, endpoint="example")
        return {
            "count": len(items),
            "items": items,
        }

    # UPDATE
    @router.add_route("/example/update", "example_update", methods=["POST"])
    @router.add_route("/example/update/<string:uid>", "example_update", methods=["POST"])
    def update(context, request, uid=None):
        items = update_items("plone.example.todo", request, uid=uid, endpoint="example")
        return {
            "count": len(items),
            "items": items,
        }

    # DELETE
    @router.add_route("/example/delete", "example_delete", methods=["POST"])
    @router.add_route("/example/delete/<string:uid>", "example_delete", methods=["POST"])
    def delete(context, request, uid=None):
        items = delete_items("plone.example.todo", request, uid=uid, endpoint="example")
        return {
            "count": len(items),
            "items": items,
        }


See it in action
----------------

A small tec demo is available on youtube:

http://www.youtube.com/watch?v=MiwgkWLMUqk


License
-------

MIT - do what you want


.. _Plone: http://plone.org
.. _Dexterity: https://pypi.python.org/pypi/plone.dexterity
.. _Werkzeug: http://werkzeug.pocoo.org
.. _plone.jsonapi.core: https://github.com/collective/plone.jsonapi.core
.. _plone.jsonapi.routes: https://github.com/collective/plone.jsonapi.routes
.. _plone.jsonapi.example: https://github.com/collective/plone.jsonapi.example
.. _mr.developer: https://pypi.python.org/pypi/mr.developer
.. _Utility: http://developer.plone.org/components/utilities.html
.. _CRUD: http://en.wikipedia.org/wiki/CRUD
.. _curl: http://curl.haxx.se/
.. _RESTful: http://en.wikipedia.org/wiki/Representational_state_transfer
.. _pypi: http://pypi.python.org

.. vim: set ft=rst ts=4 sw=4 expandtab :
