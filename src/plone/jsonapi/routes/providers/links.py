# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/links", "links", methods=["GET"])
@route("/links/<string:uid>", "links", methods=["GET"])
def get(context, request, uid=None):
    """ get links
    """
    return get_batched("Link", uid=uid, endpoint="links")


# CREATE
@route("/links/create", "links_create", methods=["POST"])
@route("/links/create/<string:uid>", "links_create", methods=["POST"])
def create(context, request, uid=None):
    """ create links
    """
    items = create_items("Link", uid=uid, endpoint="links")
    return {
        "url": url_for("links_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/links/update", "links_update", methods=["POST"])
@route("/links/update/<string:uid>", "links_update", methods=["POST"])
def update(context, request, uid=None):
    """ update links
    """
    items = update_items("Link", uid=uid, endpoint="links")
    return {
        "url": url_for("links_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/links/delete", "links_delete", methods=["POST"])
@route("/links/delete/<string:uid>", "links_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete links
    """
    items = delete_items("Link", uid=uid, endpoint="links")
    return {
        "url": url_for("links_delete"),
        "count": len(items),
        "items": items,
    }
