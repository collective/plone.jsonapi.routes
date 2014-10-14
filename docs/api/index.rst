API
===

This part of the documentation covers all resources (routes) provided by
plone.jsonapi.routes. It also covers all the request parameters that can be
applied to these resources to refine the results.


BASE URL
--------

After installation, the Plone API routes are available below the
plone.jsonapi.core root URL (``@@API``) with the base ``/plone/api/1.0``, for example
``http://localhost:8080/Plone/@@API/plone/api/1.0/api.json``.

.. note:: Please see the documentation of plone.jsonapi.core for the root URL.


There is also an overview of the registered routes which can be accessed here:

http://localhost:8080/Plone/@@API/plone/api/1.0/api.json


Operations
----------

The API understands the basic CRUD_ operations on the content resources.
Only the view operation is accessible via a HTTP GET request. All other
operations have to be sent via a HTTP POST request.

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


Resources
---------

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


Special Resources
-----------------

Beside the content URLs described above, there are some other resources
available in this extension.

+---------------+--------------------------------+
| Resource      | Description                    |
+===============+================================+
| users         | Resourece for all Plone Users  |
+---------------+--------------------------------+
| users/current | Get the current logged in user |
+---------------+--------------------------------+


Parameters
----------

All content resources accept request parameters. Basicall, all indexes from
the ``portal_catalog`` tool (`portal_catalog/manage_catalogIndexes`) can be used.

Additionally, the following request parameters can be used as well.

+-----------+------------------+------------------------------------------------------------+
| Parameter | Type             | Description                                                |
+===========+==================+============================================================+
| q         | query            | search the SearchableText index for the given query string |
+-----------+------------------+------------------------------------------------------------+
| path      | physical path    | specifiy a physical path to only return results below it   |
+-----------+------------------+------------------------------------------------------------+
| depth     | path query depth | specify the depth in combination with the path parameter   |
+-----------+------------------+------------------------------------------------------------+
| limit     | number           | limit the results to the given number                      |
+-----------+------------------+------------------------------------------------------------+



.. _CRUD: http://en.wikipedia.org/wiki/CRUD

.. vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
