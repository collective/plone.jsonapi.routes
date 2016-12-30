# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/images", "plone.jsonapi.routes.images", methods=["GET"])
@route("/images/<string:uid>", "plone.jsonapi.images", methods=["GET"])
def get(context, request, uid=None):
    """ get images
    """
    return get_batched("Image", uid=uid, endpoint="plone.jsonapi.images")


# CREATE
@route("/images/create", "plone.jsonapi.images_create", methods=["POST"])
@route("/images/create/<string:uid>", "plone.jsonapi.images_create", methods=["POST"])
def create(context, request, uid=None):
    """ create images
    """
    items = create_items("Image", uid=uid, endpoint="plone.jsonapi.images")
    return {
        "url": url_for("plone.jsonapi.images_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/images/update", "plone.jsonapi.images_update", methods=["POST"])
@route("/images/update/<string:uid>", "plone.jsonapi.images_update", methods=["POST"])
def update(context, request, uid=None):
    """ update images
    """
    items = update_items("Image", uid=uid, endpoint="plone.jsonapi.images")
    return {
        "url": url_for("plone.jsonapi.images_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/images/delete", "plone.jsonapi.routes.images_delete", methods=["POST"])
@route("/images/delete/<string:uid>", "plone.jsonapi.routes.images_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete images
    """
    items = delete_items("Image", uid=uid, endpoint="plone.jsonapi.routes.images")
    return {
        "url": url_for("plone.jsonapi.routes.images_delete"),
        "count": len(items),
        "items": items,
    }
