# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

from plone.jsonapi.routes.api import get_record


# GET
@route("/portal", "portal", methods=["GET"])
@route("/portal/<string:uid>", "portal", methods=["GET"])
def get(context, request, uid=0):
    """ get the Portal
    """
    return get_record(uid=uid)
