# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/documents", "documents", methods=["GET"])
@route("/documents/<string:uid>", "documents", methods=["GET"])
def get(context, request, uid=None):
    """ get documents
    """
    return get_batched("Document", uid=uid, endpoint="documents")


# CREATE
@route("/documents/create", "documents_create", methods=["POST"])
@route("/documents/create/<string:uid>", "documents_create", methods=["POST"])
def create(context, request, uid=None):
    """ create documents
    """
    items = create_items("Document", uid=uid, endpoint="documents")
    return {
        "url": url_for("documents_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/documents/update", "documents_update", methods=["POST"])
@route("/documents/update/<string:uid>", "documents_update", methods=["POST"])
def update(context, request, uid=None):
    """ update documents
    """
    items = update_items("Document", uid=uid, endpoint="documents")
    return {
        "url": url_for("documents_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/documents/delete", "documents_delete", methods=["POST"])
@route("/documents/delete/<string:uid>", "documents_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete documents
    """
    items = delete_items("Document", uid=uid, endpoint="documents")
    return {
        "url": url_for("documents_delete"),
        "count": len(items),
        "items": items,
    }
