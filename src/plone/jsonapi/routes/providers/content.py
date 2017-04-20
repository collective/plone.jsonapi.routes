# -*- coding: utf-8 -*-

from plone.jsonapi.routes import api
from plone.jsonapi.routes import logger
from plone.jsonapi.routes.exceptions import APIError
from plone.jsonapi.routes import add_plone_route as route


@route("/<string:resource>", "plone.jsonapi.routes.get", methods=["GET"])
@route("/<string:resource>/<string:uid>", "plone.jsonapi.routes.get", methods=["GET"])
def get(context, request, resource=None, uid=None):
    """Get Plone contents, e.g.

    <Plonesite>/@@API/plone/api/1.0/folder -> returns all folders
    <Plonesite>/@@API/plone/api/1.0/folder/4711 -> returns the folder with UID 4711
    """
    # BBB
    if resource == "get":
        logger.warn("The /get route is obsolete and will be removed in 1.0.0. Please use /<UID> instead")
        return api.get_record(uid)

    # we have a UID as resource, return the record
    if api.is_uid(resource):
        return api.get_record(resource)

    portal_type = api.resource_to_portal_type(resource)
    if portal_type is None:
        raise APIError(404, "Not Found")
    return api.get_batched(portal_type=portal_type, uid=uid, endpoint="plone.jsonapi.routes.get")


@route("/<string:action>", "plone.jsonapi.routes.action", methods=["POST"])
@route("/<string:action>/<string:uid>", "plone.jsonapi.routes.action", methods=["POST"])
@route("/<string:resource>/<string:uid>/<string:action>", "plone.jsonapi.routes.action", methods=["POST"])
def action(context, request, action=None, resource=None, uid=None):
    """Various HTTP POST actions

    Current supported actions:

      - create
      - update
      - delete
      - cut
      - copy
      - paste
    """
    # supported actions (see API function <action>_items(...))
    actions = ["create", "update", "delete", "cut", "copy", "paste"]
    if action not in actions:
        api.fail(401, "Action '{}' is not supported".format(action))

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


@route("/search", "plone.jsonapi.routes.search", methods=["GET"])
def search(context, request):
    """Generic search route

    <Plonesite>/@@API/plone/api/1.0/search -> returns all contents of the portal
    <Plonesite>/@@API/plone/api/1.0/search?portal_type=Folder -> returns only folders
    ...
    """
    return api.get_batched()
