API
===

This part of the documentation covers all resources (routes) provided by
plone.jsonapi.routes. It also covers all the request parameters that can be
applied to these resources to refine the results.


.. _Concept:

Concept
-------

The API aims to be **as fast as possible**. So the concept of the API is to
postpone *expensive operations* until the user really requests it. To do so,
the API was built with a **two step architecture**.

An *expensive operation* is basically given, when the API needs to wake up an
object to retrieve all its field values.

The *two step architecture* retrieves only the fields of the catalog results
in the first step. Only if the user requests the API URL of a specific object,
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


.. _Resources:

Resources
---------

:URL Schema: ``<BASE URL>/<RESOURCE>/<OPERATION>/<uid:optional>``

The API registers the routes to the resources during the Plone startup
process. Each of the following resources is bound to a distinct *portal type*
within Plone. So the *folders* resource will only return content informations
of *Folders*.

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

.. note:: Please see the section `Parameters` on how to refine the returned
          results


Special Resources
-----------------

:URL Schema: ``<BASE URL>/<RESOURCE>/<ACTION:optional>``

Beside the *content resources*, there are some special resources available.

+----------+--------------------+----------------------------------------+
| Resource | Action             | Description                            |
+==========+====================+========================================+
| users    | <username>,current | Resource for Plone Users               |
+----------+--------------------+----------------------------------------+
| search   |                    | Search over all standard content types |
+----------+--------------------+----------------------------------------+
| version  |                    | Get the current Version                |
+----------+--------------------+----------------------------------------+
| auth     |                    | Basic Authentication                   |
+----------+--------------------+----------------------------------------+
| login    |                    | Login with __ac_name and __ac_password |
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



.. _`Plone docs`: http://docs.plone.org/develop/plone/searching_and_indexing/query.html#query-by-path
.. _`Query by path`: http://docs.plone.org/develop/plone/searching_and_indexing/query.html#query-by-path
