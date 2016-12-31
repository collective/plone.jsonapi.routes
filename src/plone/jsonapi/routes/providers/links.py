# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/links", "plone.jsonapi.routes.links", methods=["GET"])
@route("/links/<string:uid>", "plone.jsonapi.routes.links", methods=["GET"])
def get(context, request, uid=None):
    """ get links
    """
    return get_batched("Link", uid=uid, endpoint="plone.jsonapi.routes.links")


# CREATE
@route("/links/create", "plone.jsonapi.routes.links_create", methods=["POST"])
@route("/links/create/<string:uid>", "plone.jsonapi.routes.links_create", methods=["POST"])
def create(context, request, uid=None):
    """ create links
    """
    items = create_items("Link", uid=uid, endpoint="plone.jsonapi.routes.links")
    return {
        "url": url_for("plone.jsonapi.routes.links_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/links/update", "plone.jsonapi.routes.links_update", methods=["POST"])
@route("/links/update/<string:uid>", "plone.jsonapi.routes.links_update", methods=["POST"])
def update(context, request, uid=None):
    """ update links
    """
    items = update_items("Link", uid=uid, endpoint="plone.jsonapi.routes.links")
    return {
        "url": url_for("plone.jsonapi.routes.links_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/links/delete", "plone.jsonapi.routes.links_delete", methods=["POST"])
@route("/links/delete/<string:uid>", "plone.jsonapi.routes.links_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete links
    """
    items = delete_items("Link", uid=uid, endpoint="plone.jsonapi.routes.links")
    return {
        "url": url_for("plone.jsonapi.routes.links_delete"),
        "count": len(items),
        "items": items,
    }
