# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/collections", "plone.jsonapi.routes.collections", methods=["GET"])
@route("/collections/<string:uid>", "plone.jsonapi.routes.collections", methods=["GET"])
def get(context, request, uid=None):
    """ get collections
    """
    return get_batched("Collection", uid=uid, endpoint="plone.jsonapi.routes.collections")


# CREATE
@route("/collections/create", "plone.jsonapi.routes.collections_create", methods=["POST"])
@route("/collections/create/<string:uid>", "plone.jsonapi.routes.collections_create", methods=["POST"])
def create(context, request, uid=None):
    """ create collections
    """
    items = create_items("Collection", uid=uid, endpoint="collections")
    return {
        "url": url_for("plone.jsonapi.routes.collections_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/collections/update", "plone.jsonapi.routes.collections_update", methods=["POST"])
@route("/collections/update/<string:uid>", "plone.jsonapi.routes.collections_update", methods=["POST"])
def update(context, request, uid=None):
    """ update collections
    """
    items = update_items("Collection", uid=uid, endpoint="plone.jsonapi.routes.collections")
    return {
        "url": url_for("plone.jsonapi.routes.collections_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/collections/delete", "plone.jsonapi.routes.collections_delete", methods=["POST"])
@route("/collections/delete/<string:uid>", "plone.jsonapi.routes.collections_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete collections
    """
    items = delete_items("Collection", uid=uid, endpoint="plone.jsonapi.routes.collections")
    return {
        "url": url_for("plone.jsonapi.routes.collections_delete"),
        "count": len(items),
        "items": items,
    }
