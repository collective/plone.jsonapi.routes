API
===

This part of the documentation covers all resources (routes) provided by
`plone.jsonapi.routes`_. It also covers all the request parameters that can be
applied to these resources to refine the results.


.. _Concept:

Concept
-------

The Plone JSON API aims to be **as fast as possible**. So the concept of the API
is to postpone **expensive operations** until the user really requests it. To do
so, the API was built with a **two step architecture**.

An **expensive operation** is basically given, when the API needs to "wake up"
an object to retrieve all its field values. This means the full object has to be
loaded from the Database (ZODB) into the memory (RAM).

The **two step architecture** retrieves only the fields of the catalog results
in the *first step*. Only if the user requests the API URL of a specific object,
the object will be loaded and all the fields of the object will be returned.


.. note:: Since version 0.3, you can add a `complete=yes` paramter to bypass
          the two step behavior and retrieve the full object data immediately.


.. _BASE_URL:

Base URL
--------

After installation, the Plone API routes are available below the
plone.jsonapi.core root URL (``@@API``) with the base ``/plone/api/1.0``.

Example: ``http://localhost:8080/Plone/@@API/plone/api/1.0/api.json``

.. note:: Please see the documentation of plone.jsonapi.core for the root URL.


There is also an overview of the registered routes, e.g.

``http://localhost:8080/Plone/@@API/plone/api/1.0/api.json``


.. _Resources:

Resources
---------

:URL Schema: ``<BASE URL>/<RESOURCE>/<OPERATION>/<uid:optional>``

A resource is equivalent with the portal type name in Plone.

This means that all portal types are fully supported by the API simply by adding
the portal type to the end of the base url, e.g.:

    - http://localhost:8080/Plone/@@API/plone/api/1.0/Folder
    - http://localhost:8080/Plone/@@API/plone/api/1.0/Image
    - http://localhost:8080/Plone/@@API/plone/api/1.0/File

.. note:: Lower case portal type names are also supported.


.. _Operations:

Operations
----------

The API understands the basic `CRUD <http://en.wikipedia.org/wiki/CRUD>`_
operations on the *content resources*.  Only the VIEW operation is accessible
via a HTTP GET request. All other operations have to be sent via a HTTP POST
request.

+-----------+---------------------------------------------+--------+
| OPERATION | URL                                         | METHOD |
+===========+=============================================+========+
| VIEW      | <BASE URL>/<RESOURCE>/<uid:optional>        | GET    |
+-----------+---------------------------------------------+--------+
| CREATE    | <BASE URL>/<RESOURCE>/create/<uid:optional> | POST   |
+-----------+---------------------------------------------+--------+
| UPDATE    | <BASE URL>/<RESOURCE>/update/<uid:optional> | POST   |
+-----------+---------------------------------------------+--------+
| DELETE    | <BASE URL>/<RESOURCE>/delete/<uid:optional> | POST   |
+-----------+---------------------------------------------+--------+

.. versionadded:: 0.9.1

The API is now fully aware of all registered portal types in Plone.
Each resource is now equivalent to the portal type name.

It is also possible now to get all contents by UID directly from the base url,
e.g.: http://localhost:8080/Plone/@@API/plone/api/1.0/<uid>


Search Resource
---------------

The search route omits the portal type and is therefore capable to search for
**any** content type within the portal.

The search route accepts all available indexes which are defined in the portal
catalog tool, e.g.:

    - http://localhost:8080/Plone/@@API/plone/api/1.0/search

Returns **all** contents, which were indexed by the catalog.

    - http://localhost:8080/Plone/@@API/plone/api/1.0/search?id=test

Returns contents which match the given value of the `id` parameter.


User Resource
-------------

The API is capable to find Plone users, e.g.:

    - http://localhost:8080/Plone/@@API/plone/api/1.0/users
    - http://localhost:8080/Plone/@@API/plone/api/1.0/users/current
    - http://localhost:8080/Plone/@@API/plone/api/1.0/users/<username>

.. code-block:: javascript

    {
        "count": 1,
        "pagesize": 25,
        "items": [
            {
                "username": "ramon",
                "visible_ids": false,
                "authenticated": false,
                "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/users/ramon",
                "roles": [
                    "Member",
                    "Authenticated"
                ],
                "home_page": "",
                "description": "",
                "wysiwyg_editor": "",
                "location": "",
                "error_log_update": 0,
                "language": "",
                "listed": true,
                "groups": [
                    "AuthenticatedUsers"
                ],
                "portal_skin": "",
                "fullname": "Ramon Bartl",
                "login_time": "2000-01-01T00:00:00",
                "email": "rb@ridingbytes.com",
                "ext_editor": false,
                "last_login_time": "2000-01-01T00:00:00"
            }
        ],
        "page": 1,
        "_runtime": 0.008383989334106445,
        "next": null,
        "pages": 1,
        "previous": null
    }

The results come as well as batches of 25 items per default. It is also possible
to get a higher or lower number of users per batch with the `?limit=n` request
parameter, e.g.:

http://localhost:8080/Plone/@@API/plone/api/1.0/users?limit=1

.. note:: This route lists all users for **authenticated** users only.

The username `current` is reserved to fech the current logged in user:

http://localhost:8080/Plone/@@API/plone/api/1.0/users/current

Overview
~~~~~~~~

+----------+--------------------+----------------------------------------+
| Resource | Action             | Description                            |
+==========+====================+========================================+
| users    | <username>,current | Resource for Plone Users               |
+----------+--------------------+----------------------------------------+
| auth     |                    | Basic Authentication                   |
+----------+--------------------+----------------------------------------+
| login    |                    | Login with __ac_name and __ac_password |
+----------+--------------------+----------------------------------------+
| logout   |                    | Deauthenticate                         |
+----------+--------------------+----------------------------------------+


.. _Parameters:

Parameters
----------

:URL Schema: ``<BASE URL>/<RESOURCE>?<KEY>=<VALUE>&<KEY>=<VALUE>``

All content resources accept to be filtered by request parameters.

+-----------------+-----------------------+-------------------------------------------------------------------------+
| Key             | Value                 | Description                                                             |
+=================+=======================+=========================================================================+
| q               | searchterm            | Search the SearchableText index for the given query string              |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| path            | /physical/path        | Specifiy a physical path to only return results below it.               |
|                 |                       | See how to `Query by path`_ in the `Plone docs`_ for details.           |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| depth           | 0..n                  | Specify the depth of a path query. Only relevant when using             |
|                 |                       | the path parameter.                                                     |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| limit           | 1..n                  | Limit the results to the given `limit` number.                          |
|                 |                       | This will return batched results with `x` pages and `n` items per page  |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| sort_on         | catalog index         | Sort the results by the given index                                     |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| sort_order      | asc / desc            | Sort ascending or descending (default: ascending)                       |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| sort_limit      | 1..n                  | Limit the result set to n items.                                        |
|                 |                       | The portal catalog will only return n items.                            |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| complete        | yes/y/1/True          | Flag to return the full object results immediately.                     |
|                 |                       | Bypasses the *two step* behavior of the API                             |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| children        | yes/y/1/True          | Flag to return the folder contents of a folder below the `children` key |
|                 |                       | Only visible if complete flag is true or if an UID is provided          |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| workflow        | yes/y/1/True          | Flag to include the workflow data below the `workflow` key              |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| filedata        | yes/y/1/True          | Flag to include the base64 encoded file                                 |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| recent_created  | today, yesterday      | Specify a recent created date range, to find all items created within   |
|                 | this-week, this-month | this date range until today.                                            |
|                 | this-year             | This uses internally `'range': 'min'` query.                            |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| recent_modified | today, yesterday      | Specify a recent modified date range, to find all items modified within |
|                 | this-week, this-month | this date range until today.                                            |
|                 | this-year             | This uses internally `'range': 'min'` query.                            |
+-----------------+-----------------------+-------------------------------------------------------------------------+
| sharing         | yes/y/1/True          | Flag to include the sharing rights. Only visible if complete flag is    |
|                 |                       | true.                                                                   |
+-----------------+-----------------------+-------------------------------------------------------------------------+


Using Plone Indexes
~~~~~~~~~~~~~~~~~~~

It is also possible to use the Plone catalog indexes directly as request
parameters.

.. versionadded:: 0.4
    Support for DateIndex, KeywordIndex and BooleanIndex.
    Support for 'recent_modified' and 'recent_created' literals.

.. note:: Custom added indexes can also be used, as long as they accept a
          single string value as query.


Query Records
~~~~~~~~~~~~~

It is also possible to use the ZPublisher query record format.

Example

``http://localhost:8080/Plone/@@API/plone/api/1.0/folders?created.query:record:list:date=2015-01-02&created.range:record=min``


.. versionadded:: 0.5
    Support for ZPublisher query record format added.


Sharing
~~~~~~~

It is also possible to check the sharing settings for objects

Example:

``http://localhost:8080/Plone/@@API/plone/api/1.0/folders/<uid:required>?sharing=y``
``http://localhost:8080/Plone/@@API/plone/api/1.0/folders?sharing=y&complete=y``

Response:

.. code-block:: javascript

    {
        "sharing": {
            "inherit": false,
            "role_settings": [
                {
                    "disabled": false,
                    "id": "AuthenticatedUsers",
                    "login": null,
                    "roles": {
                        "Contributor": false,
                        "Editor": false,
                        "Reader": false,
                        "Reviewer": false
                    },
                    "title": "Logged-in users",
                    "type": "group"
                }
            ]
        }
    }


Update inherit role settings:

``http://localhost:8080/Plone/@@API/plone/api/1.0/update/<uid:required>``

.. code-block:: javascript

    {
        "sharing": {
            "inherit": false,
            "role_settings": [
                {
                    "disabled": false,
                    "id": "AuthenticatedUsers",
                    "login": null,
                    "roles": {
                        "Contributor": false,
                        "Editor": false,
                        "Reader": false,
                        "Reviewer": false
                    },
                    "title": "Logged-in users",
                    "type": "group"
                }
            ]
        }
    }

.. note:: You can pass in the same format as you got from the API

.. versionadded:: 0.8.4
    Support sharing permissions of objects


.. _Response_Format:

Response Format
---------------

The response format is for all resources the same.

.. code-block:: javascript

    {
        count: 1, // number of found items
        pagesize: 25, // items per page
        items: [  // List of all item objexts
            {
                id: "front-page", // item data
                ...
            }
        ],
        page: 1, // current page
        _runtime: 0.00381,  // calculation time to generate the data
        next: null,  // URL to the next batch
        pages: 1,  //  number of total pages
        previous: null  // URL to the previous batch
    }


**count**
    The number of found items -- can be more than displayed on one site

**pagesize**
    Number of items per page

**items**
    List of found items -- only catalog brain keys unless you add a
    `complete=yes` parameter to the request or request an URL with an UID at
    the end.

**page**
    The current page of the batched result set

**_runtime**
    The time in milliseconds needed to generate the data

**next**
    The URL to the next batch

**pages**
    The number of pages in the batch

**previous**
    The URL to the previous batch


The API Module
--------------

:import: `from plone.jsonapi.routes import api`
:doc: Provides core functionality to all other modules

.. automodule:: plone.jsonapi.routes.api
   :members:
   :undoc-members:


.. Links

.. _`Plone docs`: http://docs.plone.org/develop/plone/searching_and_indexing/query.html#query-by-path
.. _`Query by path`: http://docs.plone.org/develop/plone/searching_and_indexing/query.html#query-by-path
.. _plone.jsonapi.routes: https://pypi.python.org/pypi/plone.jsonapi.routes
