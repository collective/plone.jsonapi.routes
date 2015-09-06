Example
=======

This section provides some common examples how to use `plone.jsonapi.routes`.


Get content by uid
------------------

Getting an object by its **UID**:

http://localhost:8080/Plone/@@API/plone/api/1.0/get/3762908a5d2c4917b9d2dbaf2a9be1cc


Get content by path
-------------------

Getting a content by its **physical path**:

http://localhost:8080/Plone/@@API/plone/api/1.0/get?path=/Plone/folder


Get content by parent_path and id
---------------------------------

Get a content by specifying the **parent path** and the **id**:

http://localhost:8080/Plone/@@API/plone/api/1.0/get?parent_path=/Plone&id=folder


Copy/Cut/Paste content
----------------------

Contents can be copied or cutted to the clipboard to paste it later somewhere
else. This example shows how to copy a folder located in Plone with the
physical path `/Plone/folder`.

You can either cut or copy by the `parent_path` & `id` pair:

http://localhost:8080/Plone/@@API/plone/api/1.0/copy?parent_path=/Plone&id=folder

http://localhost:8080/Plone/@@API/plone/api/1.0/cut?parent_path=/Plone&id=folder

Or you can simply take the physical path by specifying the `path`:

http://localhost:8080/Plone/@@API/plone/api/1.0/copy?path=/Plone/folder

http://localhost:8080/Plone/@@API/plone/api/1.0/cut?path=/Plone/folder

Or if you know the UID, you can use the `uid` parameter:

http://localhost:8080/Plone/@@API/plone/api/1.0/copy/3762908a5d2c4917b9d2dbaf2a9be1cc

http://localhost:8080/Plone/@@API/plone/api/1.0/cut/3762908a5d2c4917b9d2dbaf2a9be1cc

After you cutted or copied the content, you can paste it by providing the
target folder in the known way.

If you would like to paste it in the portal root, just use the UID 0 or the path of
your Plone site:

http://localhost:8080/Plone/@@API/plone/api/1.0/paste/0

http://localhost:8080/Plone/@@API/plone/api/1.0/paste?path=/Plone


Search contents
---------------

To search **all** contents of the portal, you can utilize the `search` route:

http://localhost:8080/Plone/@@API/plone/api/1.0/search

The search results can be refined by using request parameters, e.g.:

http://localhost:8080/Plone/@@API/plone/api/1.0/search?q=test

http://localhost:8080/Plone/@@API/plone/api/1.0/search?q=test&limit=10

http://localhost:8080/Plone/@@API/plone/api/1.0/search?q=test&limit=10&portal_type=Folder

http://localhost:8080/Plone/@@API/plone/api/1.0/search?q=test&limit=10&portal_type=Folder&Creator=admin

Basically, you can use any defined index of your Plone site.

There are some convenience keys like `q` for the SearchableText index.
See :ref:`Parameters` for further details.


Delete contents
---------------

It is possible to delete contents from your Plone site with the `delete` route.
See :doc:`crud` for details.

You can either delete by the `parent_path` & `id` pair:

http://localhost:8080/Plone/@@API/plone/api/1.0/delete?parent_path=/Plone&id=folder

Or you can simply take the physical path by specifying the `path`:

http://localhost:8080/Plone/@@API/plone/api/1.0/delete?path=/Plone/folder

Or if you know the UID, you can use the `uid` parameter:

http://localhost:8080/Plone/@@API/plone/api/1.0/delete/3762908a5d2c4917b9d2dbaf2a9be1cc


It is even possible to delete multiple objects. This can be done by sending the
data in a list within the POST body. See :doc:`crud` for mode details.

.. note:: The API do not allow to delete the portal object (UID=0)


Get the portal object
---------------------

To fetch the portal object you can use the `plonesites` route. Despite the
pluralized name, there can be only one responsible plone site for the API at a
time.

There are two ways to fetch the portal, either as a single record or in the default
response format specified by :ref:`Response_Format`.

To get a single result record, you have to use the `portal` route:

http://localhost:8080/Plone/@@API/plone/api/1.0/portal

To get the known `items` response format as specified in :ref:`Response_Format`, you
have to use the `plonesites` route:

http://localhost:8080/Plone/@@API/plone/api/1.0/plonesites


Get folder contents
-------------------

If you are interested in the contents of a folderish content type, you can
append the `children=yes` request parameter to the url:

http://localhost:8080/Plone/@@API/plone/api/1.0/plonesites?children=yes

this will add a `children` list to the response which includes all contents of
the requested object. This can actually be done with any route provider.


Get the full object
-------------------

The API is designed in a two step architecture, see the API doc:`Concept`. Therefore
only the catlog brain results are returned in the first step.

You can bypass this step by specifying the `complete=yes` request parameter.

.. note:: The `complete=yes` parameter also affects the child nodes


.. note:: It is not recommended to use the complete flag, as it is significant slower.
