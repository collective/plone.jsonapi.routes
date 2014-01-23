plone.jsonapi.routes
====================

:Author: Ramon Bartl
:Version: 0.1


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

The plone.jsonapi.routes_ should work with Plone_ 3 and 4.


Installation
------------

The official release is on pypi, so you have to simply include
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

+-----------+---------------------------------------------+--------+---------+
| OPERATION | URL                                         | METHOD | PAYLOAD |
+===========+=============================================+========+=========+
| VIEW      | <BASE_URL>/<RESOURCE>/<uid:optional>        | GET    | --      |
+-----------+---------------------------------------------+--------+---------+
| CREATE    | <BASE_URL>/<RESOURCE>/create/<uid:optional> | POST   | JSON    |
+-----------+---------------------------------------------+--------+---------+
| UPDATE    | <BASE_URL>/<RESOURCE>/update/<uid:optional> | POST   | JSON    |
+-----------+---------------------------------------------+--------+---------+
| DELETE    | <BASE_URL>/<RESOURCE>/delete/<uid:optional> | POST   | JSON    |
+-----------+---------------------------------------------+--------+---------+

.. important:: the optional UID of the create, update and delete URLs is to
               specify the target container where to create the content.  If
               this is omitted, the API expects a parameter `parent_uid` in the
               request body JSON. If this is also not found, an API Error will
               be returned.


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


Folders
~~~~~~~

:RESOURCE: `folders`

API Resource for `Folders`

+--------+---------------------------+------+
| VIEW   | <BASE_URL>/folders/       | GET  |
+--------+---------------------------+------+
| CREATE | <BASE_URL>/folders/create | POST |
+--------+---------------------------+------+
| UPDATE | <BASE_URL>/folders/update | POST |
+--------+---------------------------+------+
| DELETE | <BASE_URL>/folders/delete | POST |
+--------+---------------------------+------+


Documents
~~~~~~~~~

:RESOURCE: `documents`

API Resource for `Documents`

+--------+-----------------------------+------+
| VIEW   | <BASE_URL>/documents/       | GET  |
+--------+-----------------------------+------+
| CREATE | <BASE_URL>/documents/create | POST |
+--------+-----------------------------+------+
| UPDATE | <BASE_URL>/documents/update | POST |
+--------+-----------------------------+------+
| DELETE | <BASE_URL>/documents/delete | POST |
+--------+-----------------------------+------+


Events
~~~~~~

:RESOURCE: `events`


API Resource for `Events`

+--------+--------------------------+------+
| VIEW   | <BASE_URL>/events/       | GET  |
+--------+--------------------------+------+
| CREATE | <BASE_URL>/events/create | POST |
+--------+--------------------------+------+
| UPDATE | <BASE_URL>/events/update | POST |
+--------+--------------------------+------+
| DELETE | <BASE_URL>/events/delete | POST |
+--------+--------------------------+------+


Files
~~~~~

:RESOURCE: `files`

API Resource for `Files`

+--------+-------------------------+------+
| VIEW   | <BASE_URL>/files/       | GET  |
+--------+-------------------------+------+
| CREATE | <BASE_URL>/files/create | POST |
+--------+-------------------------+------+
| UPDATE | <BASE_URL>/files/update | POST |
+--------+-------------------------+------+
| DELETE | <BASE_URL>/files/delete | POST |
+--------+-------------------------+------+


Images
~~~~~~

:RESOURCE: `images`

API Resource for `Images`

+--------+--------------------------+------+
| VIEW   | <BASE_URL>/images/       | GET  |
+--------+--------------------------+------+
| CREATE | <BASE_URL>/images/create | POST |
+--------+--------------------------+------+
| UPDATE | <BASE_URL>/images/update | POST |
+--------+--------------------------+------+
| DELETE | <BASE_URL>/images/delete | POST |
+--------+--------------------------+------+


Links
~~~~~

:RESOURCE: `links`

API Resource for `Links`

+--------+-------------------------+------+
| VIEW   | <BASE_URL>/links/       | GET  |
+--------+-------------------------+------+
| CREATE | <BASE_URL>/links/create | POST |
+--------+-------------------------+------+
| UPDATE | <BASE_URL>/links/update | POST |
+--------+-------------------------+------+
| DELETE | <BASE_URL>/links/delete | POST |
+--------+-------------------------+------+


News Items
~~~~~~~~~~

:RESOURCE: `newsitems`

API Resource for `News Items`

+--------+-----------------------------+------+
| VIEW   | <BASE_URL>/newsitems/       | GET  |
+--------+-----------------------------+------+
| CREATE | <BASE_URL>/newsitems/create | POST |
+--------+-----------------------------+------+
| UPDATE | <BASE_URL>/newsitems/update | POST |
+--------+-----------------------------+------+
| DELETE | <BASE_URL>/newsitems/delete | POST |
+--------+-----------------------------+------+


Topics
~~~~~~

:RESOURCE: `topics`

API Resource for `Topics`

+--------+--------------------------+------+
| VIEW   | <BASE_URL>/topics/       | GET  |
+--------+--------------------------+------+
| CREATE | <BASE_URL>/topics/create | POST |
+--------+--------------------------+------+
| UPDATE | <BASE_URL>/topics/update | POST |
+--------+--------------------------+------+
| DELETE | <BASE_URL>/topics/delete | POST |
+--------+--------------------------+------+


Collections
~~~~~~~~~~~

:RESOURCE: `collections`

API Resource for `Collections`

+--------+-------------------------------+------+
| VIEW   | <BASE_URL>/collections/       | GET  |
+--------+-------------------------------+------+
| CREATE | <BASE_URL>/collections/create | POST |
+--------+-------------------------------+------+
| UPDATE | <BASE_URL>/collections/update | POST |
+--------+-------------------------------+------+
| DELETE | <BASE_URL>/collections/delete | POST |
+--------+-------------------------------+------+


Users
~~~~~

:RESOURCE: `users`

API Resource for `Plone Users`

+-------------+--------------------------+-----+
| VIEW        | <BASE_URL>/users         | GET |
+-------------+--------------------------+-----+
| GET CURRENT | <BASE_URL>/users/current | GET |
+-------------+--------------------------+-----+


Examples
--------

These examples show the basic usage of the API.
All examples are done from the command line using curl_.

.. important:: Using curl_ without the `--cookie` parameter acts like an anonymous
               request. So the contents of the Plone site need to be published.
               To create/update/delelete contents in Plone, the curl_ requests
               need to be authenticated. Thus, I copied the `__ac` cookie value
               from my browser to the `--cookie` parameter of curl_.

Imagine an empty Plone site with just 2 Folders:

    - Folder 1
    - Folder 2

Now lets list these folder. Therefore we use the `documents` resource of the API::

    curl -XGET http://localhost:8080/Plone/@@API/plone/api/1.0/folders | python -mjson.tool

    {
        "_runtime": 0.0024950504302978516,
        "count": 2,
        "items": [
            {
                "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders/1b3e6ccde22b48778d5af5768ee49983",
                "created": "2014-01-23T10:10:53+01:00",
                "description": "The first Folder",
                "effective": "2014-01-23T10:11:15+01:00",
                "id": "folder-1",
                "modified": "2014-01-23T10:11:15+01:00",
                "portal_type": "Folder",
                "tags": [],
                "title": "Folder 1",
                "type": "Folder",
                "uid": "1b3e6ccde22b48778d5af5768ee49983",
                "url": "http://localhost:8080/Plone/folder-1"
            },
            {
                "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders/0198f943bd2b48a8970b04d637f74888",
                "created": "2014-01-23T10:11:05+01:00",
                "description": "The second Folder",
                "effective": "2014-01-23T10:11:15+01:00",
                "id": "folder-2",
                "modified": "2014-01-23T10:11:15+01:00",
                "portal_type": "Folder",
                "tags": [],
                "title": "Folder 2",
                "type": "Folder",
                "uid": "0198f943bd2b48a8970b04d637f74888",
                "url": "http://localhost:8080/Plone/folder-2"
            }
        ],
        "url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders"
    }

As you can see, the two folders get listed. Also note, that for reasons of
performance, the request to a root URL of a resource contains only the catalog
results. The objects don't get waked up until we request a specific item.

Now we will request a specific folder, which will wake up the object to show more detailed informations::

    curl -XGET http://localhost:8080/Plone/@@API/plone/api/1.0/folders/1b3e6ccde22b48778d5af5768ee49983 | python -mjson.tool

    {
        "_runtime": 0.008948087692260742,
        "count": 1,
        "items": [
            {
                "allowDiscussion": false,
                "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders/1b3e6ccde22b48778d5af5768ee49983",
                "constrainTypesMode": 0,
                "contributors": [],
                "created": "2014-01-23T10:10:53+01:00",
                "creation_date": "2014-01-23T10:10:53+01:00",
                "creators": [
                    "admin"
                ],
                "description": "The first Folder",
                "effective": "2014-01-23T10:11:15+01:00",
                "effectiveDate": "2014-01-23T10:11:15+01:00",
                "excludeFromNav": false,
                "expirationDate": null,
                "id": "folder-1",
                "immediatelyAddableTypes": [],
                "language": "de",
                "locallyAllowedTypes": [],
                "location": "",
                "modification_date": "2014-01-23T10:11:15+01:00",
                "modified": "2014-01-23T10:11:15+01:00",
                "nextPreviousEnabled": false,
                "parent_id": "Plone",
                "parent_uid": 0,
                "portal_type": "Folder",
                "relatedItems": [],
                "rights": "",
                "subject": [],
                "tags": [],
                "title": "Folder 1",
                "type": "Folder",
                "uid": "1b3e6ccde22b48778d5af5768ee49983",
                "url": "http://localhost:8080/Plone/folder-1"
            }
        ],
        "url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders"
    }

The response of a specific resource is much more detailed since we gather the
schema fields of the object.  Also note, that if the content is located below
the Plone site root, the parent_uid will be 0.

Now lets create a document below this folder. Therefore, the request needs to
be authenticated. I simply "steal" the **__ac** cookie value of my
authenticated browser session::

    curl -XPOST -H "Content-Type: application/json" -d '{"parent_uid":"1b3e6ccde22b48778d5af5768ee49983", "title":"A Document below Folder 1"}' http://localhost:8080/Plone/@@API/plone/api/1.0/documents/create  --cookie "__ac=NjE2NDZkNjk2ZTo2MTY0NmQ2OTZl" | python -mjson.tool

    {
        "_runtime": 0.08417892456054688,
        "count": 1,
        "items": [
            {
                "allowDiscussion": false,
                "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/c1b61148a3a3489c9ae5f18a8b552ceb",
                "contributors": [],
                "creation_date": "2014-01-23T11:54:02+01:00",
                "creators": [
                    "admin"
                ],
                "description": "",
                "effectiveDate": null,
                "excludeFromNav": false,
                "expirationDate": null,
                "id": "a-document-below-folder-1",
                "language": "de",
                "location": "",
                "modification_date": "2014-01-23T11:54:02+01:00",
                "parent_id": "folder-1",
                "parent_uid": "1b3e6ccde22b48778d5af5768ee49983",
                "parent_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders/1b3e6ccde22b48778d5af5768ee49983",
                "presentation": false,
                "relatedItems": [],
                "rights": "",
                "subject": [],
                "tableContents": false,
                "text": "",
                "title": "A Document below Folder 1"
            }
        ],
        "url": "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/create"
    }

Note how the `parent_uid` is updated to the one of `Folder 1` and the generated
`api_url` points to the correct `folders` resource here.

Now lets update this document. Therefore we post a new JSON object with the
informations to the documents api url::

    curl -XPOST -H "Content-Type: application/json" -d '{"uid": "c1b61148a3a3489c9ae5f18a8b552ceb", "description":"The description changed", "text": "Some Text"}' http://localhost:8080/Plone/@@API/plone/api/1.0/documents/update  --cookie "__ac=NjE2NDZkNjk2ZTo2MTY0NmQ2OTZl" | python -mjson.tool

    {
        "_runtime": 0.049546003341674805,
        "count": 1,
        "items": [
            {
                "allowDiscussion": false,
                "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/c1b61148a3a3489c9ae5f18a8b552ceb",
                "contributors": [],
                "creation_date": "2014-01-23T11:54:02+01:00",
                "creators": [
                    "admin"
                ],
                "description": "The description changed",
                "effectiveDate": null,
                "excludeFromNav": false,
                "expirationDate": null,
                "id": "a-document-below-folder-1",
                "language": "de",
                "location": "",
                "modification_date": "2014-01-23T12:11:33+01:00",
                "parent_id": "folder-1",
                "parent_uid": "1b3e6ccde22b48778d5af5768ee49983",
                "parent_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/folders/1b3e6ccde22b48778d5af5768ee49983",
                "presentation": false,
                "relatedItems": [],
                "rights": "",
                "subject": [],
                "tableContents": false,
                "text": "<p>Some Text</p>",
                "title": "A Document below Folder 1"
            }
        ],
        "url": "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/update"
    }

Note how the description and text changed!

Finally, lets delete the item::

    curl -XPOST -H "Content-Type: application/json" -d '{"uid": "c1b61148a3a3489c9ae5f18a8b552ceb"}' http://localhost:8080/Plone/@@API/plone/api/1.0/documents/delete  --cookie "__ac=NjE2NDZkNjk2ZTo2MTY0NmQ2OTZl" | python -mjson.tool

    {
        "_runtime": 0.0047149658203125,
        "count": 1,
        "items": [
            {
                "deleted": true,
                "id": "a-document-below-folder-1"
            }
        ],
        "url": "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/delete"
    }

The document is now gone::

    curl -XGET http://localhost:8080/Plone/@@API/plone/api/1.0/documents | python -mjson.tool

    {
        "_runtime": 0.0019440650939941406,
        "count": 0,
        "items": [],
        "url": "http://localhost:8080/Plone/@@API/plone/api/1.0/documents"
    }


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
.. _CRUD: http://en.wikipedia.org/wiki/CRUD
.. _curl: http://curl.haxx.se/
.. _RESTful: http://en.wikipedia.org/wiki/Representational_state_transfer

.. vim: set ft=rst ts=4 sw=4 expandtab :
