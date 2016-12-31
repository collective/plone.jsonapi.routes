# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route
from plone.jsonapi.routes.api import get_record


# GET (default route)
@route("/get", "plone.jsonapi.routes.get", methods=["GET"])
@route("/get/<string:uid>", "plone.jsonapi.routes.get", methods=["GET"])
def get(context, request, uid=None):
    """ get content
    """
    return get_record(uid=uid)
