# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

from plone.jsonapi.routes.api import get_record

from plone.jsonapi.routes.api import url_for


# GET
@route("/plonesites", "plonesites", methods=["GET"])
@route("/plonesites/<string:uid>", "plonesites", methods=["GET"])
def get(context, request, uid=None):
    """ Plone sites
    """

    # There is always only one portal
    portal = get_record(uid="Portal")
    # only show the portal record if an uid was passed in
    # the uid can be anything here;)
    if uid is not None:
        return portal

    # otherwise show the same structure like for the other content types
    items = [portal]
    return {
        "url": url_for("plonesites"),
        "count": len(items),
        "items": items,
        }
