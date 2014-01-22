# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/newsitems", "newsitems", methods=["GET"])
@add_plone_route("/newsitems/<string:uid>", "newsitems", methods=["GET"])
def get(context, request, uid=None):
    """ get newsitems
    """
    items = get_items("News Item", request, uid=uid, endpoint="newsitems")
    return {
        "url": url_for("newsitems"),
        "count": len(items),
        "items": items,
    }


# CREATE
@add_plone_route("/newsitems/create", "newsitems_create", methods=["POST"])
@add_plone_route("/newsitems/create/<string:uid>", "newsitems_create", methods=["POST"])
def create(context, request, uid=None):
    """ create newsitems
    """
    items = create_items("News Item", request, uid=uid, endpoint="newsitems")
    return {
        "url": url_for("newsitems_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/newsitems/update", "newsitems_update", methods=["POST"])
@add_plone_route("/newsitems/update/<string:uid>", "newsitems_update", methods=["POST"])
def update(context, request, uid=None):
    """ update newsitems
    """
    items = update_items("News Item", request, uid=uid, endpoint="newsitems")
    return {
        "url": url_for("newsitems_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/newsitems/delete", "newsitems_delete", methods=["POST"])
@add_plone_route("/newsitems/delete/<string:uid>", "newsitems_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete newsitems
    """
    items = delete_items("News Item", request, uid=uid, endpoint="newsitems")
    return {
        "url": url_for("newsitems_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
