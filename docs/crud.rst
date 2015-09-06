CRUD
====

Each content route provider shipped with this package, provides the basic CRUD
:ref:`Operations` functionality to `get`, `create`, `delete` and `update` the
resource handled.

.. versionadded:: 0.8.1
    Added route providers to `cut`, `copy` and `paste` contents


Unified API
-----------

:URL Schema: ``<BASE URL>/<OPERATION>/<uid:optional>``

There is a convenient and unified way to fetch the content without knowing the
resource. This unified resource is directly located at the :ref:`BASE_URL`.


Response Format
---------------

The response format of the unified `get` API differs from the default
:ref:`Response_Format` and omits the `items` list. The content information is
directly provided in the root of the returned JSON object.
Therefore it is only suitable to return a single object.


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
    Adding 0 or the string `portal` as UID returns the portal Object.


CREATE
------

The `create` route will create the content inside the container located at the
given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/create/<uid:optional>

The given optional UID defines the target container. You can omit this UID
and specify all the information in the HTTP POST body.

Example
.......

This example shows possible variations of a HTTP POST body sent to the JSON
API with the header **Content-Type: application/json** set.

.. code-block:: javascript

    {
        portal_type: "Document", // mandatory
        id: "test", // mandatory if title is not set
        title: "test", // mandatory if id is not set
        parent_uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can specify the UID for the parent folder
        parent_path: "/Plone/folder", // or the physical path of the parent container
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

Delete an object by its **physical path**:

http://localhost:8080/Plone/@@API/plone/api/1.0/delete?path=/Plone/folder

Or you can specify the **parent path** and the **id** of the object

http://localhost:8080/Plone/@@API/plone/api/1.0/delete?parent_path=/Plone&id=folder

Or you can specify these information in the request body:

.. code-block:: javascript

    {
        uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can either specify the UID
        path: "/Plone/folder/test", // or the physical path to the object
        id: "test", // or the id and the path of the parent container
        parent_path: "/Plone/folder",
        ...
    }


CUT
---

The `cut` route will cut the content located at the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/cut/<uid:optional>

The given optional UID defines the object to cut. You can omit this UID and
specify all the information either in the HTTP POST body or as request arguments.

Example
.......

Cut an object by its **physical path**:

http://localhost:8080/Plone/@@API/plone/api/1.0/cut?path=/Plone/folder

Or you can specify the **parent path** and the **id** of the object

http://localhost:8080/Plone/@@API/plone/api/1.0/cut?parent_path=/Plone&id=folder

Or you can specify these information in the request body:

.. code-block:: javascript

    {
        uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can either specify the UID
        path: "/Plone/folder/test", // or the physical path to the object
        id: "test", // or the id and the path of the parent container
        parent_path: "/Plone/folder",
        ...
    }


COPY
----

The `copy` route will copy the content located at the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/copy/<uid:optional>

The given optional UID defines the object to copy. You can omit this UID and
specify all the information either in the HTTP POST body or as request arguments.

Example
.......

Copy an object by its **physical path**:

http://localhost:8080/Plone/@@API/plone/api/1.0/copy?path=/Plone/folder

Or you can specify the **parent path** and the **id** of the object

http://localhost:8080/Plone/@@API/plone/api/1.0/copy?parent_path=/Plone&id=folder

Or you can specify these information in the request body:

.. code-block:: javascript

    {
        uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can either specify the UID
        path: "/Plone/folder/test", // or the physical path to the object
        id: "test", // or the id and the path of the parent container
        parent_path: "/Plone/folder",
        ...
    }


PASTE
-----

The `paste` route will paste the previous cutted/copied content to the location
identified by the given UID.

http://localhost:8080/Plone/@@API/plone/api/1.0/paste/<uid:optional>

The given optional UID defines the target object (usually a folder). You can
omit this UID and specify all the information either in the HTTP POST body or
as request arguments.

Example
.......

Paste to a target identified by its **physical path**:

http://localhost:8080/Plone/@@API/plone/api/1.0/paste?path=/Plone/folder

Or you can specify the **parent path** and the **id** of the object

http://localhost:8080/Plone/@@API/plone/api/1.0/paste?parent_path=/Plone&id=folder

Or you can specify these information in the request body:

.. code-block:: javascript

    {
        uid: "7455c9b14e3c48c9b0be19ca6a142d50", // you can either specify the UID
        path: "/Plone/folder/test", // or the physical path to the object
        id: "test", // or the id and the path of the parent container
        parent_path: "/Plone/folder",
        ...
    }
