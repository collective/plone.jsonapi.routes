Quickstart
==========

This chapter gives a good introduction about `plone.jsonapi.routes` It assumes
you already have Flask installed. Since all the coming examples are executed
directly in Google Chrome, it assumes that you have also installed JSONView and the
Advanced Rest Client Application.


Environment
-----------

The Plone site is hosted on `http://localhost:8080/Plone`. The JSON API is thus
located at `http://localhost:8080/Plone/@@API/plone/api/1.0`. Make sure your Plone
site is located on the same URL, so you can directly click on the links within the
exapmles.


Version
-------

The `version` route prints out the current version of `plone.jsonapi.routes.`

http://localhost:8080/Plone/@@API/plone/api/1.0/version

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/version",
        date: "2014-10-14",
        version: "0.4",
        build: 130,
        _runtime: 0.0019528865814208984
    }


Overview
--------

The `api.json` route gives you an overview over all registered routes.

http://localhost:8080/Plone/@@API/plone/api/1.0/api.json

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/api.json",
        count: 11,
        _runtime: 0.0027348995208740234,
        items: [
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/collections",
                info: "get collections",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents",
                info: "No description available",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/newsitems",
                info: "get newsitems",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/folders",
                info: "get folders",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/version",
                info: "get the current version of this package",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/events",
                info: "get events",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/images",
                info: "get images",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/topics",
                info: "get topics",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/files",
                info: "get files",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/links",
                info: "get links",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/users",
                info: "Plone users route",
                methods: "HEAD,GET"
            }
        ]
    }


Content Routes
--------------

Coming now to a more interesting section, the content routes - giving you the
ultimative power over the default Plone content types.


Documents
~~~~~~~~~

The `documents` route will rule all contents of the portal type `Document`.

http://localhost:8080/Plone/@@API/plone/api/1.0/documents

.. code-block:: javascript

    {
        count: 1,
        pagesize: 25,
        items: [
            {
                uid: "7455c9b14e3c48c9b0be19ca6a142d50",
                tags: [ ],
                portal_type: "Document",
                id: "front-page",
                description: "Herzlichen Glückwunsch! Sie haben das professionelle Open-Source Content-Management-System Plone erfolgreich installiert.",
                api_url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/7455c9b14e3c48c9b0be19ca6a142d50",
                effective: "1000-01-01T00:00:00+02:00",
                title: "Willkommen bei Plone",
                url: "http://localhost:8080/Plone/front-page",
                created: "2014-10-14T20:22:19+02:00",
                modified: "2014-10-14T20:22:19+02:00",
                type: "Document"
            }
        ],
        page: 1,
        _runtime: 0.0038590431213378906,
        next: null,
        pages: 1,
        previous: null
    }

The response format in `plone.jsonapi.routes` content URLs is always the same.
The top level
keys (data after the first ``{``) are meta informations about the gathered data.

Since version `0.3`, the items always batched. This means you get the items
split up into batches onto multiple sites.

The definition list below will get you some guidance how to interpret the data:

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


Within the **items** list, you get all the results listed. It is important to
know, that these records contain only the minimum set of data from the catalog
brains. This is because of the APIs **two step** concept, which postpones
expensive opreations, until the user really wants it.


.. vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
