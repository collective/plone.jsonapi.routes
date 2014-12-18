# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_record
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/get", "get", methods=["GET"])
@add_plone_route("/get/<string:uid>", "get", methods=["GET"])
def get(context, request, uid=None):
    """ get content
    """
    return get_record(uid=uid)


# CREATE
@add_plone_route("/create", "create", methods=["POST"])
@add_plone_route("/create/<string:uid>", "create", methods=["POST"])
def create(context, request, uid=None):
    """ create content
    """
    items = create_items(uid=uid)
    return {
        "url": url_for("create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/update", "update", methods=["POST"])
@add_plone_route("/update/<string:uid>", "update", methods=["POST"])
def update(context, request, uid=None):
    """ update content
    """
    items = update_items(uid=uid)
    return {
        "url": url_for("update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/delete", "delete", methods=["POST"])
@add_plone_route("/delete/<string:uid>", "delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete content
    """
    items = delete_items(uid=uid)
    return {
        "url": url_for("delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
