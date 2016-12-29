# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/documents", "plone.jsonapi.routes.documents", methods=["GET"])
@route("/documents/<string:uid>", "plone.jsonapi.routes.documents", methods=["GET"])
def get(context, request, uid=None):
    """ get documents
    """
    return get_batched("Document", uid=uid, endpoint="plone.jsonapi.routes.documents")


# CREATE
@route("/documents/create", "plone.jsonapi.routes.documents_create", methods=["POST"])
@route("/documents/create/<string:uid>", "plone.jsonapi.routes.documents_create", methods=["POST"])
def create(context, request, uid=None):
    """ create documents
    """
    items = create_items("Document", uid=uid, endpoint="plone.jsonapi.routes.documents")
    return {
        "url": url_for("plone.jsonapi.routes.documents_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/documents/update", "plone.jsonapi.routes.documents_update", methods=["POST"])
@route("/documents/update/<string:uid>", "plone.jsonapi.routes.documents_update", methods=["POST"])
def update(context, request, uid=None):
    """ update documents
    """
    items = update_items("Document", uid=uid, endpoint="plone.jsonapi.routes.documents")
    return {
        "url": url_for("plone.jsonapi.routes.documents_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/documents/delete", "plone.jsonapi.routes.documents_delete", methods=["POST"])
@route("/documents/delete/<string:uid>", "plone.jsonapi.routes.documents_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete documents
    """
    items = delete_items("Document", uid=uid, endpoint="plone.jsonapi.routes.documents")
    return {
        "url": url_for("plone.jsonapi.routes.documents_delete"),
        "count": len(items),
        "items": items,
    }
