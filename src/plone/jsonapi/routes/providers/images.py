# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/images", "images", methods=["GET"])
@route("/images/<string:uid>", "images", methods=["GET"])
def get(context, request, uid=None):
    """ get images
    """
    return get_batched("Image", uid=uid, endpoint="images")


# CREATE
@route("/images/create", "images_create", methods=["POST"])
@route("/images/create/<string:uid>", "images_create", methods=["POST"])
def create(context, request, uid=None):
    """ create images
    """
    items = create_items("Image", uid=uid, endpoint="images")
    return {
        "url": url_for("images_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/images/update", "images_update", methods=["POST"])
@route("/images/update/<string:uid>", "images_update", methods=["POST"])
def update(context, request, uid=None):
    """ update images
    """
    items = update_items("Image", uid=uid, endpoint="images")
    return {
        "url": url_for("images_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/images/delete", "images_delete", methods=["POST"])
@route("/images/delete/<string:uid>", "images_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete images
    """
    items = delete_items("Image", uid=uid, endpoint="images")
    return {
        "url": url_for("images_delete"),
        "count": len(items),
        "items": items,
    }
