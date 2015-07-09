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

    # CREATE
    @add_route("/todos/create", "todos_create", methods=["POST"])
    @add_route("/todos/create/<string:uid>", "todos_create", methods=["POST"])
    def create(context, request, uid=None):
        """ create todos
        """
        items = create_items("Todo", uid=uid, endpoint="todos")
        return {
            "url": url_for("todos_create"),
            "count": len(items),
            "items": items,
        }

    # UPDATE
    @add_route("/todos/update", "todos_update", methods=["POST"])
    @add_route("/todos/update/<string:uid>", "todos_update", methods=["POST"])
    def update(context, request, uid=None):
        """ update todos
        """
        items = update_items("Todo", uid=uid, endpoint="todos")
        return {
            "url": url_for("todos_update"),
            "count": len(items),
            "items": items,
        }

    # DELETE
    @add_route("/todos/delete", "todos_delete", methods=["POST"])
    @add_route("/todos/delete/<string:uid>", "todos_delete", methods=["POST"])
    def delete(context, request, uid=None):
        """ delete todos
        """
        items = delete_items("Todo", uid=uid, endpoint="todos")
        return {
            "url": url_for("todos_delete"),
            "count": len(items),
            "items": items,
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

Adding a custom  data manager
-----------------------------

The data sent by the API for each content type is set by the `IDataManager`
Adapter. This Adapter has a simple interface:

.. code-block:: python

    class IDataManager(interface.Interface):
        """ Field Interface
        """

        def get(name): """ Get the value of the named field with
            """

        def set(name, value):
            """ Set the value of the named field
            """

To customize how the data is set to each field of the content, you have to
register an adapter for a more specific interface on the content.
This adapter has to implement the `IDataManager` interface.


.. important:: Please be aware that you have to implement security for field
               level access by your own.

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
