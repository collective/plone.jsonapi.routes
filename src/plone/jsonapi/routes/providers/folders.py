# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/folders", "plone.jsonapi.routes.folders", methods=["GET"])
@route("/folders/<string:uid>", "plone.jsonapi.routes.folders", methods=["GET"])
def get(context, request, uid=None):
    """ get folders
    """
    return get_batched("Folder", uid=uid, endpoint="plone.jsonapi.routes.folders")


# CREATE
@route("/folders/create", "plone.jsonapi.routes.folders_create", methods=["POST"])
@route("/folders/create/<string:uid>", "plone.jsonapi.routes.folders_create", methods=["POST"])
def create(context, request, uid=None):
    """ create folders
    """
    items = create_items("Folder", uid=uid, endpoint="plone.jsonapi.routes.folders")
    return {
        "url": url_for("plone.jsonapi.routes.folders_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/folders/update", "plone.jsonapi.routes.folders_update", methods=["POST"])
@route("/folders/update/<string:uid>", "plone.jsonapi.routes.folders_update", methods=["POST"])
def update(context, request, uid=None):
    """ update folders
    """
    items = update_items("Folder", uid=uid, endpoint="plone.jsonapi.routes.folders")
    return {
        "url": url_for("plone.jsonapi.routes.folders_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/folders/delete", "plone.jsonapi.routes.folders_delete", methods=["POST"])
@route("/folders/delete/<string:uid>", "plone.jsonapi.routes.folders_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete folders
    """
    items = delete_items("Folder", uid=uid, endpoint="plone.jsonapi.routes.folders")
    return {
        "url": url_for("plone.jsonapi.routes.folders_delete"),
        "count": len(items),
        "items": items,
    }
