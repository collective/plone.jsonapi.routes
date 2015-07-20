Authentication
==============

Since version 0.8 (see: :ref:`Changelog`) the API provides a simple way to
authenticate a user with Plone.


Login
-----

:URL Schema: ``<BASE URL>/login?__ac_name=<username>&__ac_password=<password>``

The response will set the `__ac` cookie for further cookie authenticated requests.

.. note:: Currently only cookie authentication works. Other PAS plugins might
          not work as expected.

Example

``http://localhost:8080/Plone/@@API/plone/api/1.0/login?__ac_name=admin&__ac_password=admin``

Response

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/users",
        count: 1,
        _runtime: 0.0019960403442382812,
        items: [
            {
                username: "admin",
                authenticated: true,
                last_login_time: "",
                roles: [
                    "Manager",
                    "Authenticated"
                ],
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/users/admin",
                email: null,
                groups: [ ],
                fullname: null,
                id: "admin",
                login_time: ""
            }
        ]
    }


Logout
------

:URL Schema: ``<BASE URL>/logout``

The response will expire the `__ac` cookie for further requests.

Example

``http://localhost:8080/Plone/@@API/plone/api/1.0/logout``

Response

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/users",
        _runtime: 0.0009028911590576172,
        success: true
    }


Basic Authentication
--------------------

:URL Schema: ``<BASE URL>/auth``

If the reqeust is not authenticated, this route will raise an unauthorized
response with status code 401. Browsers should display the Basic Authentication
login.
Example

``http://localhost:8080/Plone/@@API/plone/api/1.0/auth``
