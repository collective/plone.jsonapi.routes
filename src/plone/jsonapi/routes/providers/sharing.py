# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# Sharing
from plone.jsonapi.routes.api import get_sharing
from plone.jsonapi.routes.api import update_sharing

from plone.jsonapi.routes.api import url_for


# GET
@route("/sharing", "sharing_get", methods=["GET"])
@route("/sharing/<string:uid>", "sharing_get", methods=["GET"])
def get(context, request, uid=None):
    """ get sharing
    """
    items = get_sharing(request, uid)
    return {
        "url": url_for("sharing"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/sharing/update", "sharing_update", methods=["POST"])
@route("/sharing/update/<string:uid>", "sharing_update",
       methods=["POST"])
def update(context, request, uid=None):
    """ update todos
    """
    items = update_sharing(request=request, uid=uid)
    return {
        "url": url_for("sharing_update"),
        "count": len(items),
        "items": items,
    }
