# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

from plone.jsonapi.routes.api import get_batched


# GET
@route("/plonesites", "plonesites", methods=["GET"])
@route("/plonesites/<string:uid>", "plonesites", methods=["GET"])
def get(context, request, uid=None):
    """ Plone sites
    """
    return get_batched("Plone Site", uid=uid, endpoint="plonesites")
