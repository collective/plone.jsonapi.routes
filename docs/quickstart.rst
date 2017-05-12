Quickstart
==========

This section gives a good introduction about `plone.jsonapi.routes`_. It assumes
you already have `Plone`_ and `plone.jsonapi.routes`_ installed. Since all the
coming examples are executed directly in Google Chrome, it assumes that you have
also installed `JSONView`_ and the `Advanced Rest Client`_ Application (see
:doc:`installation` for details)


Environment
-----------

The Plone site is hosted on `http://localhost:8080/Plone`. The JSON API is
therefore located at `http://localhost:8080/Plone/@@API/plone/api/1.0`. Make
sure your Plone site is located on the same URL, so you can directly click on
the links within the exapmles.


Version
-------

The `version` route prints out the current version of `plone.jsonapi.routes`.

http://localhost:8080/Plone/@@API/plone/api/1.0/version

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/version",
        date: "2017-05-12",
        version: "0.9.2",
        _runtime: 0.0001528865814208984
    }

.. note:: The runtime indicates the time spent in milliseconds until the
          response is prepared.


Content Routes
--------------

These :ref:`Resources` are automatically generated for **all** available content
types in Plone.

Each content route is located at the :ref:`BASE_URL`, e.g.

  - http://localhost:8080/Plone/@@API/plone/api/1.0/folder
  - http://localhost:8080/Plone/@@API/plone/api/1.0/image
  - http://localhost:8080/Plone/@@API/plone/api/1.0/file
  - http://localhost:8080/Plone/@@API/plone/api/1.0/document
  - http://localhost:8080/Plone/@@API/plone/api/1.0/collection
  - http://localhost:8080/Plone/@@API/plone/api/1.0/<myportaltype>

The name of each of these content routes is transformed to lower case, so it is
also perfectly ok to call these :ref:`Resources` like so:

  - http://localhost:8080/Plone/@@API/plone/api/1.0/Folder
  - http://localhost:8080/Plone/@@API/plone/api/1.0/Image
  - http://localhost:8080/Plone/@@API/plone/api/1.0/File
  - http://localhost:8080/Plone/@@API/plone/api/1.0/Document
  - http://localhost:8080/Plone/@@API/plone/api/1.0/Collection
  - http://localhost:8080/Plone/@@API/plone/api/1.0/<MyPortalType>

Calling a content route like this will return a JSON format similar to this:

.. code-block:: javascript

    {
        count: 14,
        pagesize: 25,
        items: [
            {},
            {},
            {},
            {},
            ...
        ],
        page: 1,
        _runtime: 0.0038590431213378906,
        next: null,
        pages: 1,
        previous: null
    }

The :ref:`Response_Format` in `plone.jsonapi.routes` content URLs is always the
same. The top level keys (data after the first ``{``) are meta informations
about the gathered data.

The `items` list will contain the list of catalog results for the portal type
requested. This means that each result contains just the metadata available in
the catalog. Therfore, no object is "waked up" to retrieve the data at this stage.
This is because of the APIs **two step** concept, which postpones expensive
opreations, until the user really wants it.

All `items` are batched to increase performance of the API. The `count` number
returns the total number objects found, while the `page` number returns the
number of pages in the batch, which can be navigated with the `next` and
`previous` links.

.. versionadded:: 0.3
    The result is now always batched. This means you get
    the items split up into batches onto multiple sites.


Getting the Full Data
~~~~~~~~~~~~~~~~~~~~~

To get all data from an object, you can either add the ``complete=True``
parameter, or you can request the data with the object ``UID``.

  - http://localhost:8080/Plone/@@API/plone/api/1.0/folder?complete=True
  - http://localhost:8080/Plone/@@API/plone/api/1.0/image/<uid>
  - http://localhost:8080/Plone/@@API/plone/api/1.0/<uid>

The requested content(s) is now loaded by the API and all fields were gathered.

.. note:: Please keep in mind that large data sets with the `?complete=True`
          Parameter might increase the loading time significantly.


Special Case: Files and Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - http://localhost:8080/Plone/@@API/plone/api/1.0/file
  - http://localhost:8080/Plone/@@API/plone/api/1.0/image

.. versionadded:: 0.2
    The object data contains now the base64 encoded file with the size and
    mimetype information.

.. versionadded:: 0.7
    You can pass in a `filename` in the JSON body to set the name of the file
    created. If omitted, the id or title will be used.

.. versionadded:: 0.8
    You can pass in a `mimetype` key to manually set the content type of the
    file. If omitted, the content type will be guessed by the filename.
    Default: `application/octet-stream`

.. versionadded:: 0.8
    The response data contains now the `filename` and the `download` url.


To create a new file in the portal, you have to HTTP POST to the `create` route:

http://localhost:8080/Plone/@@API/plone/api/1.0/file/create

The HTTP POST payload can look like this:

.. code-block:: javascript

    {
        "title": "Test.docx",
        "description": "A Word File",
        "filename": "test.docx",
        "parent_path": "/Plone/folder",
        "file":"UEsDBBQABgAIAAA..."
    }

The `file` key in the HTTP POST payload contains the `base64` encoded content of
the file/image.


UID Route
---------

To fetch the full data of an object immediately, it is also possible to append
the UID of the object directly on the root URL of the API, e.g.:

    - http://localhost:8080/Plone/@@API/plone/api/1.0/553ce5b2c55847a08dea2a7016a0e11a
    - http://localhost:8080/Plone/@@API/plone/api/1.0/document/c79c878703194ee78944c36dedd7b26d

.. note:: The given UID might seem different on your machine.

The response will give the data in the root of the JSON data, e.g.:

.. code-block:: javascript

    {
        "uid": "553ce5b2c55847a08dea2a7016a0e11a",
        "contributors": [],
        "file": "http://localhost:8080/Plone/w7614.pdf/@@download/file/w7614.pdf",
        "_runtime": 0.010680913925170898,
        "exclude_from_nav": false,
        "id": "w7614.pdf",
        "api_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/file/553ce5b2c55847a08dea2a7016a0e11a",
        "title": "w7614.pdf",
        "parent_id": "Plone",
        "subjects": null,
        "author": "admin",
        "parent_url": "http://localhost:8080/Plone/@@API/plone/api/1.0/plonesite/0",
        "description": "",
        "tags": [],
        "portal_type": "File",
        "expires": null,
        "relatedItems": [],
        "parent_uid": "0",
        "effective": null,
        "language": "",
        "rights": "",
        "url": "http://localhost:8080/Plone/w7614.pdf",
        "created": "2017-05-12T12:47:38+02:00",
        "modified": "2017-05-12T12:47:38+02:00",
        "allow_discussion": null,
        "creators": [
            "admin"
        ]
    }


.. Links

.. _Plone: http://plone.org
.. _plone.jsonapi.routes: https://pypi.python.org/pypi/plone.jsonapi.routes
.. _Advanced Rest Client: https://chrome.google.com/webstore/detail/advanced-rest-client
.. _JSONView: https://chrome.google.com/webstore/detail/jsonview
.. _
