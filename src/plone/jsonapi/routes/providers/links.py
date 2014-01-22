# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/links", "links", methods=["GET"])
@add_plone_route("/links/<string:uid>", "links", methods=["GET"])
def get(context, request, uid=None):
    """ get links
    """
    items = get_items("Link", request, uid=uid, endpoint="links")
    return {
        "url": url_for("links"),
        "count": len(items),
        "items": items,
    }


# CREATE
@add_plone_route("/links/create", "links_create", methods=["POST"])
@add_plone_route("/links/create/<string:uid>", "links_create", methods=["POST"])
def create(context, request, uid=None):
    """ create links
    """
    items = create_items("Link", request, uid=uid, endpoint="links")
    return {
        "url": url_for("links_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/links/update", "links_update", methods=["POST"])
@add_plone_route("/links/update/<string:uid>", "links_update", methods=["POST"])
def update(context, request, uid=None):
    """ update links
    """
    items = update_items("Link", request, uid=uid, endpoint="links")
    return {
        "url": url_for("links_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/links/delete", "links_delete", methods=["POST"])
@add_plone_route("/links/delete/<string:uid>", "links_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete links
    """
    items = delete_items("Link", request, uid=uid, endpoint="links")
    return {
        "url": url_for("links_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
