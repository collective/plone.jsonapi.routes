# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_record
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items
from plone.jsonapi.routes.api import cut_items
from plone.jsonapi.routes.api import copy_items
from plone.jsonapi.routes.api import paste_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/get", "get", methods=["GET"])
@route("/get/<string:uid>", "get", methods=["GET"])
def get(context, request, uid=None):
    """ get content
    """
    return get_record(uid=uid)


# CREATE
@route("/create", "create", methods=["POST"])
@route("/create/<string:uid>", "create", methods=["POST"])
def create(context, request, uid=None):
    """ create content
    """
    items = create_items(uid=uid, request=request)
    return {
        "url": url_for("create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/update", "update", methods=["POST"])
@route("/update/<string:uid>", "update", methods=["POST"])
def update(context, request, uid=None):
    """ update content
    """
    items = update_items(uid=uid, request=request)
    return {
        "url": url_for("update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/delete", "delete", methods=["GET", "POST"])
@route("/delete/<string:uid>", "delete", methods=["GET", "POST"])
def delete(context, request, uid=None):
    """ delete content
    """
    items = delete_items(uid=uid, request=request)
    return {
        "url": url_for("delete"),
        "count": len(items),
        "items": items,
    }


# CUT
@route("/cut", "cut", methods=["GET", "POST"])
@route("/cut/<string:uid>", "cut", methods=["GET", "POST"])
def cut(context, request, uid=None):
    """ cut content
    """
    items = cut_items(uid=uid, request=request)
    return {
        "url": url_for("cut"),
        "count": len(items),
        "items": items,
    }


# COPY
@route("/copy", "copy", methods=["GET", "POST"])
@route("/copy/<string:uid>", "copy", methods=["GET", "POST"])
def copy(context, request, uid=None):
    """ copy content
    """
    items = copy_items(uid=uid, request=request)
    return {
        "url": url_for("copy"),
        "count": len(items),
        "items": items,
    }


# PASTE
@route("/paste", "paste", methods=["GET", "POST"])
@route("/paste/<string:uid>", "paste", methods=["GET", "POST"])
def paste(context, request, uid=None):
    """ paste content
    """
    items = paste_items(uid=uid, request=request)
    return {
        "url": url_for("paste"),
        "count": len(items),
        "items": items,
    }
