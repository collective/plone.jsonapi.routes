# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/files", "files", methods=["GET"])
@route("/files/<string:uid>", "files", methods=["GET"])
def get(context, request, uid=None):
    """ get files
    """
    return get_batched("File", request, uid=uid, endpoint="files")


# CREATE
@route("/files/create", "files_create", methods=["POST"])
@route("/files/create/<string:uid>", "files_create", methods=["POST"])
def create(context, request, uid=None):
    """ create files
    """
    items = create_items("File", request, uid=uid, endpoint="files")
    return {
        "url": url_for("files_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/files/update", "files_update", methods=["POST"])
@route("/files/update/<string:uid>", "files_update", methods=["POST"])
def update(context, request, uid=None):
    """ update files
    """
    items = update_items("File", request, uid=uid, endpoint="files")
    return {
        "url": url_for("files_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/files/delete", "files_delete", methods=["POST"])
@route("/files/delete/<string:uid>", "files_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete files
    """
    items = delete_items("File", request, uid=uid, endpoint="files")
    return {
        "url": url_for("files_delete"),
        "count": len(items),
        "items": items,
    }
