# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/folders", "folders", methods=["GET"])
@add_plone_route("/folders/<string:uid>", "folders", methods=["GET"])
def get(context, request, uid=None):
    """ get folders
    """
    items = get_items("Folder", request, uid=uid, endpoint="folders")
    return {
        "url": url_for("folders"),
        "count": len(items),
        "items": items,
    }


# CREATE
@add_plone_route("/folders/create", "folders_create", methods=["POST"])
@add_plone_route("/folders/create/<string:uid>", "folders_create", methods=["POST"])
def create(context, request, uid=None):
    """ create folders
    """
    items = create_items("Folder", request, uid=uid, endpoint="folders")
    return {
        "url": url_for("folders_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/folders/update", "folders_update", methods=["POST"])
@add_plone_route("/folders/update/<string:uid>", "folders_update", methods=["POST"])
def update(context, request, uid=None):
    """ update folders
    """
    items = update_items("Folder", request, uid=uid, endpoint="folders")
    return {
        "url": url_for("folders_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/folders/delete", "folders_delete", methods=["POST"])
@add_plone_route("/folders/delete/<string:uid>", "folders_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete folders
    """
    items = delete_items("Folder", request, uid=uid, endpoint="folders")
    return {
        "url": url_for("folders_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
