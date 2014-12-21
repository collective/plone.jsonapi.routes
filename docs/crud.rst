CRUD
====

Each route provider shipped with this package, provides the basic CRUD
:ref:`Operations` functionality to `get`, `create`, `delete` and `update` the
resource handled.


Unified API
-----------

:URL Schema: ``<BASE URL>/<OPERATION>/<uid:optional>``

There is a convenient and unified way to fetch the content without knowing the
resource. This unified resource is directly located at the :ref:`BASE_URL`.


Response Format
---------------

The response format differs from the default :ref:`Response_Format` and omits
the `items` list. The content information is directly provided in the root of
the JSON object.


.. code-block:: javascript

    {
        _runtime: 0.00381,
        uid: "7455c9b14e3c48c9b0be19ca6a142d50",
        tags: [ ],
        portal_type: "Document",
        id: "front-page",
        description: "Welcome to Plone",
        api_url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/7455c9b14e3c48c9b0be19ca6a142d50",
        effective: "1000-01-01T00:00:00+02:00",
        title: "Welcome to Plone",
        url: "http://localhost:8080/Plone/front-page",
        created: "2014-10-14T20:22:19+02:00",
        modified: "2014-10-14T20:22:19+02:00",
        type: "Document"
    }


GET
---

The `get` route will return the content located at the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/get/<uid:optional>

The given optional UID defines the target object to get. You can omit this UID
and specify the path to the object with a request parameter.

Example
.......

Getting an object by its **physical path**:

http://localhost:8080/Plone/@@API/plone/api/1.0/get?path=/Plone/folder

Or you can specify the **parent path** and the **id** of the object

http://localhost:8080/Plone/@@API/plone/api/1.0/get?parent_path=/Plone&id=folder


.. versionadded:: 0.4
    Adding 0 as UID returns the portal Object.


CREATE
------

The `create` route will create the content located at the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/create/<uid:optional>

The given optional UID defines the target container. You can omit this UID
and specify all the information in the HTTP POST body.

Example
.......

.. code-block:: javascript

    {
        portal_type: "Document", // mandatory
        id: "test", // mandatory if title is not set
        title: "test", // mandatory if id is not set
        parent_uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can specify the UID for the parent folder
        parent_path: "/plone/folder", // or the physical path of the parent container
        ...
    }



UPDATE
------

The `update` route will update the content located at the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/update/<uid:optional>

The given optional UID defines the object to update. You can omit this UID and
specify all the information in the HTTP POST body.

Example
.......

.. code-block:: javascript

    {
        uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can either specify the UID
        path: "/Plone/folder/test", // or the physical path to the object
        id: "test", // or the id and the path of the parent container
        parent_path: "/Plone/folder",
        ...
    }


DELETE
------

The `delete` route will delete the content located at the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/delete/<uid:optional>

The given optional UID defines the object to delete. You can omit this UID and
specify all the information in the HTTP POST body.

Example
.......

.. code-block:: javascript

    {
        uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can either specify the UID
        path: "/Plone/folder/test", // or the physical path to the object
        id: "test", // or the id and the path of the parent container
        parent_path: "/Plone/folder",
        ...
    }

.. vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
