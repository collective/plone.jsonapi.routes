Customizing
===========

This package is built to be extended. You can either use the `Zope Component
Architecture` and provide an specific Adapter to control what is being returned
by the API or you simply write your own route provider.

This section will show how to build a custom route provider for an example
content type. It will also show how to write and register a custom data adapter
for this content type. It is even possible to customize how the fields of a
specific content type can be accessed or modified.

.. _ROUTE_PROVIDER:

Adding a custom route provider
------------------------------

Each route provider shipped with this package, provides the basic CRUD
functionality to `get`, `create`, `delete` and `update` the resource handled.

The same functionality can be used to provide this behavior for custom content
types. All neccessary functions are located in the `api` module within this
package.


.. code-block:: python

    # CRUD
    from plone.jsonapi.routes.api import get_batched
    from plone.jsonapi.routes.api import create_items
    from plone.jsonapi.routes.api import update_items
    from plone.jsonapi.routes.api import delete_items

    # route dispatcher
    from plone.jsonapi.core.browser.router import add_route

    # GET
    @add_route("/todos", "todos", methods=["GET"])
    @add_route("/todos/<string:uid>", "todos", methods=["GET"])
    def get(context, request, uid=None):
        """ get all todos
        """
        return get_batched("Todo", uid=uid, endpoint="todo")


.. versionadded:: 0.3
    The standard GET route returns now the results for all resoures batched.
    This behavior is provided by the `get_batched` function.

.. note:: The prior `get_items` function, which returns all items in an array,
          is still provided, but not recommended due to performance issues.

.. versionadded:: 0.9.0
    You can specify an own `query` and pass it to the `get_batched` or
    `get_items` funciton of the api. This gives full control over the executed
    query on the catalog. Please see the `docs/Readme.rst` doctest for more
    details.

.. example::

    @add_route("/myquery", "myquery", methods=["GET"])
    def myquery(context, request):
        """ get all todos
        """
        return get_batched(query={"portal_type": "Document"})

.. note:: Other keywords (except `uid`) are ignored, if the `query` keyword is
          detected.

The upper example registers a function named `get` with the `add_route`
decorator. This ensures that this function gets called when the `/todos` route
is called, e.g. `http://localhost:8080/Plone/@@API/todo`.

The second argument of the decorator is the endpoint, which is kind of the
registration key for our function. The last argument is the methods we would
like to handle here. In this case we're only interested in GET requests.

All route providers get always the `context` and the `request` as the first two
arguments.  The `uid` keyword argument is passed in, when a UID was appended to
the URL, e.g `http://localhost:8080/Plone/@@API/todo/a3f3f9efd0b4df190d16ea63d`.

The `get_batched` function we call inside our function will do all the heavy
lifting for us.  We simply need to pass in the `portal_type` as the first
argument, the `UID` and the `endpoint`.

To be able to create, update and delete our `Todo` content type, it is
neccessary to provide the following functions as well. The behavior is analogue
to the upper example but as there is no need for batching, the functions return
a Python `<list>` instead of a complete mapping as above.


.. code-block:: python

    ACTIONS = "create,update,delete,cut,copy,paste"

    # http://werkzeug.pocoo.org/docs/0.11/routing/#builtin-converters
    # http://werkzeug.pocoo.org/docs/0.11/routing/#custom-converters
    @route("/<any(" + ACTIONS + "):action>",
          "plone.jsonapi.routes.action", methods=["POST"])
    @route("/<any(" + ACTIONS + "):action>/<string(maxlength=32):uid>",
          "plone.jsonapi.routes.action", methods=["POST"])
    @route("/<string:resource>/<any(" + ACTIONS + "):action>",
          "plone.jsonapi.routes.action", methods=["POST"])
    @route("/<string:resource>/<any(" + ACTIONS + "):action>/<string(maxlength=32):uid>",
          "plone.jsonapi.routes.action", methods=["POST"])
    def action(context, request, action=None, resource=None, uid=None):
        """Various HTTP POST actions

        Case 1: <action>
        <Plonesite>/@@API/plone/api/1.0/<action>

        Case 2: <action>/<uid>
        -> The actions (cut, copy, update, delete) will performed on the object identified by <uid>
        -> The actions (create, paste) will use the <uid> as the parent folder
        <Plonesite>/@@API/plone/api/1.0/<action>/<uid>

        Case 3: <resource>/<action>
        -> The "target" object will be located by a location given in the request body (uid, path, parent_path + id)
        -> The actions (cut, copy, update, delete) will performed on the target object
        -> The actions (create) will use the target object as the container
        <Plonesite>/@@API/plone/api/1.0/<resource>/<action>

        Case 4: <resource>/<action>/<uid>
        -> The actions (cut, copy, update, delete) will performed on the object identified by <uid>
        -> The actions (create) will use the <uid> as the parent folder
        <Plonesite>/@@API/plone/api/1.0/<resource>/<action>
        """

        # Fetch and call the action function of the API
        func_name = "{}_items".format(action)
        action_func = getattr(api, func_name, None)
        if action_func is None:
            api.fail(500, "API has no member named '{}'".format(func_name))

        portal_type = api.resource_to_portal_type(resource)
        items = action_func(portal_type=portal_type, uid=uid)

        return {
            "count": len(items),
            "items": items,
            "url": api.url_for("plone.jsonapi.routes.action", action=action),
        }


Adding a custom  data adapter
-----------------------------

The data returned by the API for each content type is extracted by the `IInfo`
Adapter. This Adapter simply extracts all field values from the content.

To customize how the data is extracted from the content, you have to register an
adapter for a more specific interface on the content.

This adapter has to implement the `IInfo` interface.

.. code-block:: python

    from plone.jsonapi.routes.interfaces import IInfo

    class TodoAdapter(object):
        """ A custom adapter for Todo content types
        """
        interface.implements(IInfo)

        def __init__(self, context):
            self.context = context

        def to_dict(self):
            return {} # whatever data you need

        def __call__(self):
            # just implement it like this, don't ask x_X
            return self.to_dict()

Register the adapter in your `configure.zcml` file for your special interface:

.. code-block:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope">

        <!-- Adapter for my custom content type -->
        <adapter
            for="plone.todo.interfaces.ITodo"
            factory=".adapters.TodoAdapter"
            />

    </configure>


.. _DATA_MANAGER:

Adding a custom data manager
----------------------------

The data sent by the API for **each content type** is set by the `IDataManager`
Adapter. This Adapter has a simple interface:

.. code-block:: python

    class IDataManager(interface.Interface):
        """ Field Interface
        """

        def get(name):
            """ Get the value of the named field with
            """

        def set(name, value):
            """ Set the value of the named field
            """

        def json_data(name, default=None):
            """ Get a JSON compatible structure from the value
            """

To customize how the data is set to each field of the content, you have to
register an adapter for a more specific interface on the content.
This adapter has to implement the `IDataManager` interface.

.. note:: The `json_data` function is called by the Data Provider Adapter
          (`IInfo`) to get a JSON compatible return Value, e.g.:
          DateTime('2017/05/14 14:46:18.746800 GMT+2') -> "2017-05-14T14:46:18+02:00"


.. important:: Please be aware that you have to implement security for field
               level access on your own.

.. code-block:: python

    from zope.annotation import IAnnotations
    from persistent.dict import PersistentDict
    from plone.jsonapi.routes.interfaces import IDataManager

    class TodoDataManager(object):
        """ A custom data manager for Todo content types
        """
        interface.implements(IDataManager)

        def __init__(self, context):
            self.context = context

        @property
        def storage(self):
            return IAnnotations(self.context).setdefault('plone.todo', PersistentDict())

        def get(self, name):
            self.storage.get("name")

        def set(self, name, value):
            self.storage["name"] = value


Register the adapter in your `configure.zcml` file for your special interface:

.. code-block:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope">

        <!-- Adapter for my custom content type -->
        <adapter
            for="plone.todo.interfaces.ITodo"
            factory=".adapters.TodoDataManager"
            />

    </configure>


.. _FIELD_MANAGER:

Adding a custom field manager
-----------------------------

The default data managers (`IDataManager`) defined in this package know how to
`set` and `get` the values from fields. But sometimes it might be useful to be
more granular and know how to `set` and `get` a value for a **specific field**.

Therefore, `plone.jsonapi.routes` introduces Field Managers (`IFieldManager`),
which adapt a field.

This Adapter has a simple interface:

.. code-block:: python

    class IFieldManager(interface.Interface):
        """A Field Manager is able to set/get the values of a single field.
        """

        def get(instance, **kwargs):
            """Get the value of the field
            """

        def set(instance, value, **kwargs):
            """Set the value of the field
            """

        def json_data(instance, default=None):
            """Get a JSON compatible structure from the value
            """

To customize how the data is set to each field of the content, you have to
register a more specific adapter to a field.

This adapter has to implement then the `IFieldManager` interface.

.. note:: The `json_data` function is called by the Data Manager Adapter
          (`IDataManager`) to get a JSON compatible return Value, e.g.:
          DateTime('2017/05/14 14:46:18.746800 GMT+2') -> "2017-05-14T14:46:18+02:00"

.. note:: The `json_data` method is defined on context level (`IDataManger`) as
          well as on field level (`IFieldManager`). This is to handle objects
          w/o fields, e.g. Catalog Brains, Portal Object etc. and Objects which
          contain fields and want to delegate the JSON representation to the
          field.

.. important:: Please be aware that you have to implement security for field
               level access on your own.

.. code-block:: python

    class DateTimeFieldManager(ATFieldManager):
        """Adapter to get/set the value of DateTime Fields
        """
        interface.implements(IFieldManager)

        def set(self, instance, value, **kw):
            """Converts the value into a DateTime object before setting.
            """
            try:
                value = DateTime(value)
            except SyntaxError:
                logger.warn("Value '{}' is not a valid DateTime string"
                            .format(value))
                return False

            self._set(instance, value, **kw)

        def json_data(self, instance, default=None):
            """Get a JSON compatible value
            """
            value = self.get(instance)
            return api.to_iso_date(value) or default

Register the adapter in your `configure.zcml` file for your special interface:

.. code-block:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope">

      <!-- Adapter for AT DateTime Field -->
      <adapter
          for="Products.Archetypes.interfaces.field.IDateTimeField"
          factory=".fieldmanagers.DateTimeFieldManager"
          />

    </configure>


.. _CATALOG:

Adding a custom catalog tool
----------------------------

.. versionadded:: 0.9.1
    You can specify an own `catalog` tool which performs your custom query.

All search is done through a catalog adapter. This adapter has to provide at
least a `search` method. The others are optional, but recommended.

.. code-block:: python

    class ICatalog(interface.Interface):
        """ Plone catalog interface
        """

        def search(query):
            """ search the catalog and return the results
            """

        def get_catalog():
            """ get the used catalog tool
            """

        def get_indexes():
            """ get all indexes managed by this catalog
            """

        def get_index(name):
            """ get an index by name
            """

        def to_index_value(value, index):
            """ Convert the value for a given index
            """

To customize the catalog tool to get full control of the search, you have to
register an catalog adapter for a more specific interface on the portal. This
adapter has to implement the `ICatalog` interface.


.. code-block:: python

    from zope import interface
    from plone.jsonapi.routes.interfaces import ICatalog
    from plone.jsonapi.routes import api

    class Catalog(object):
        """Plone catalog adapter
        """
        interface.implements(ICatalog)

        def __init__(self, context):
            self._catalog = api.get_tool("portal_catalog")

        def search(self, query):
            """search the catalog
            """
            catalog = self.get_catalog()
            return catalog(query)

Register the adapter in your `configure.zcml` file for your special interface:

.. code-block:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope">

        <!-- Adapter for a custom catalog adapter -->
        <adapter
            for=".interfaces.ICustomPortalMarkerInterface"
            factory=".catalog.Catalog"
            />

    </configure>


.. _CATALOG_QUERY:

Adding a custom catalog query adapter
-------------------------------------

.. versionadded:: 0.9.1
    You can specify an own `query` adapter, which builds a query for the catalog adapter.

All search is done through a catalog adapter. The `ICatalogQuery` adapter
provides a suitable query usable for the `ICatalog` adapter. It should at least
provide a `make_query` method.

.. code-block:: python

    class ICatalogQuery(interface.Interface):
        """ Plone catalog query interface
        """

        def make_query(**kw):
            """ create a new query or augment an given query
            """

To customize a custom catalog tool to perform a search, you have to
register an catalog adapter for a more specific interface on the portal.
This adapter has to implement the `ICatalog` interface.


.. code-block:: python

    from zope import interface
    from plone.jsonapi.routes.interfaces import ICatalogQuery

    class CatalogQuery(object):
        """Catalog query adapter
        """
        interface.implements(ICatalogQuery)

        def __init__(self, catalog):
            self.catalog = catalog

        def make_query(self, **kw):
            """create a query suitable for the catalog
            """
            query = {"sort_on": "created", "sort_order": "descending"}
            query.update(kw)
            return query

Register the adapter in your `configure.zcml` file for your special interface:

.. code-block:: xml

    <configure
        xmlns="http://namespaces.zope.org/zope">

        <!-- Adapter for a custom query adapter -->
        <adapter
            for=".interface.ICustomCatalogInterface"
            factory=".catalog.CatalogQuery"
            />

    </configure>
