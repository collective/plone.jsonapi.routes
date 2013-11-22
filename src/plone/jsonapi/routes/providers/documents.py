# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from plone.jsonapi.routes.api import url_for
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items


# GET
@router.add_route("/documents", "documents", methods=["GET"])
@router.add_route("/documents/<string:uid>", "documents", methods=["GET"])
def documents(context, request, uid=None):
    """ get documents
    """
    items = get_items("Document", request, uid=uid, endpoint="documents")
    return {
        "url": url_for("documents"),
        "count": len(items),
        "items": items,
    }


# CREATE
@router.add_route("/documents/create", "documents_create", methods=["POST"])
@router.add_route("/documents/create/<string:uid>", "documents_create", methods=["POST"])
def documents_create(context, request, uid=None):
    """ create documents
    """
    items = create_items("Document", request, uid=uid, endpoint="documents")
    return {
        "url": url_for("documents_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@router.add_route("/documents/update", "documents_update", methods=["POST"])
@router.add_route("/documents/update/<string:uid>", "documents_update", methods=["POST"])
def documents_update(context, request, uid=None):
    """ update documents
    """
    items = update_items("Document", request, uid=uid, endpoint="documents")
    return {
        "url": url_for("documents_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@router.add_route("/documents/delete", "documents_delete", methods=["POST"])
@router.add_route("/documents/delete/<string:uid>", "documents_delete", methods=["POST"])
def documents_delete(context, request, uid=None):
    """ delete documents
    """
    items = delete_items("Document", request, uid=uid, endpoint="documents")
    return {
        "url": url_for("documents_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
