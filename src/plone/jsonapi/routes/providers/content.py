# -*- coding: utf-8 -*-

from plone.jsonapi.routes import api
from plone.jsonapi.routes import logger
from plone.jsonapi.routes.exceptions import APIError
from plone.jsonapi.routes import add_plone_route as route

ACTIONS = "create,update,delete,cut,copy,paste"


@route("/<string:resource>",
       "plone.jsonapi.routes.get", methods=["GET"])
@route("/<string:resource>/<string(maxlength=32):uid>",
       "plone.jsonapi.routes.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """Get Plone contents, e.g.

    <Plonesite>/@@API/plone/api/1.0/folder -> returns all folders
    <Plonesite>/@@API/plone/api/1.0/folder/4711 -> returns the folder with UID 4711
    """
    # we have a UID as resource, return the record
    if api.is_uid(resource):
        return api.get_record(resource)

    # BBB
    if resource == "get":
        logger.warn("The /get route is obsolete and will be removed in 1.0.0. Please use /<UID> instead")
        return api.get_record(uid)

    portal_type = api.resource_to_portal_type(resource)
    if portal_type is None:
        raise APIError(404, "Not Found")
    return api.get_batched(portal_type=portal_type, uid=uid, endpoint="plone.jsonapi.routes.get")


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


@route("/search",
       "plone.jsonapi.routes.search", methods=["GET"])
def search(context, request):
    """Generic search route

    <Plonesite>/@@API/plone/api/1.0/search -> returns all contents of the portal
    <Plonesite>/@@API/plone/api/1.0/search?portal_type=Folder -> returns only folders
    ...
    """
    return api.get_batched()
