# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items
from plone.jsonapi.routes.api import cut_items
from plone.jsonapi.routes.api import copy_items
from plone.jsonapi.routes.api import paste_items

from plone.jsonapi.routes.api import url_for


# CREATE
@route("/create", "plone.jsonapi.routes.create", methods=["POST"])
@route("/create/<string:uid>", "plone.jsonapi.routes.create", methods=["POST"])
def create(context, request, uid=None):
    """ create content
    """
    items = create_items(uid=uid)
    return {
        "url": url_for("plone.jsonapi.routes.create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/update", "plone.jsonapi.routes.update", methods=["POST"])
@route("/update/<string:uid>", "plone.jsonapi.routes.update", methods=["POST"])
def update(context, request, uid=None):
    """ update content
    """
    items = update_items(uid=uid)
    return {
        "url": url_for("plone.jsonapi.routes.update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/delete", "plone.jsonapi.routes.delete", methods=["GET", "POST"])
@route("/delete/<string:uid>", "deplone.jsonapi.routes.lete", methods=["GET", "POST"])
def delete(context, request, uid=None):
    """ delete content
    """
    items = delete_items(uid=uid)
    return {
        "url": url_for("plone.jsonapi.routes.delete"),
        "count": len(items),
        "items": items,
    }


# CUT
@route("/cut", "plone.jsonapi.routes.cut", methods=["GET", "POST"])
@route("/cut/<string:uid>", "plone.jsonapi.routes.cut", methods=["GET", "POST"])
def cut(context, request, uid=None):
    """ cut content
    """
    items = cut_items(uid=uid)
    return {
        "url": url_for("plone.jsonapi.routes.cut"),
        "count": len(items),
        "items": items,
    }


# COPY
@route("/copy", "plone.jsonapi.routes.copy", methods=["GET", "POST"])
@route("/copy/<string:uid>", "plone.jsonapi.routes.copy", methods=["GET", "POST"])
def copy(context, request, uid=None):
    """ copy content
    """
    items = copy_items(uid=uid)
    return {
        "url": url_for("plone.jsonapi.routes.copy"),
        "count": len(items),
        "items": items,
    }


# PASTE
@route("/paste", "plone.jsonapi.routes.paste", methods=["GET", "POST"])
@route("/paste/<string:uid>", "plone.jsonapi.routes.paste", methods=["GET", "POST"])
def paste(context, request, uid=None):
    """ paste content
    """
    items = paste_items(uid=uid)
    return {
        "url": url_for("plone.jsonapi.routes.paste"),
        "count": len(items),
        "items": items,
    }
