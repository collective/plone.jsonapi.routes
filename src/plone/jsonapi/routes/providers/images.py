# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/images", "images", methods=["GET"])
@add_plone_route("/images/<string:uid>", "images", methods=["GET"])
def get(context, request, uid=None):
    """ get images
    """
    items = get_items("Image", request, uid=uid, endpoint="images")
    return {
        "url": url_for("images"),
        "count": len(items),
        "items": items,
    }


# CREATE
@add_plone_route("/images/create", "images_create", methods=["POST"])
@add_plone_route("/images/create/<string:uid>", "images_create", methods=["POST"])
def create(context, request, uid=None):
    """ create images
    """
    items = create_items("Image", request, uid=uid, endpoint="images")
    return {
        "url": url_for("images_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/images/update", "images_update", methods=["POST"])
@add_plone_route("/images/update/<string:uid>", "images_update", methods=["POST"])
def update(context, request, uid=None):
    """ update images
    """
    items = update_items("Image", request, uid=uid, endpoint="images")
    return {
        "url": url_for("images_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/images/delete", "images_delete", methods=["POST"])
@add_plone_route("/images/delete/<string:uid>", "images_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete images
    """
    items = delete_items("Image", request, uid=uid, endpoint="images")
    return {
        "url": url_for("images_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
