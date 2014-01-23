# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/topics", "topics", methods=["GET"])
@add_plone_route("/topics/<string:uid>", "topics", methods=["GET"])
def get(context, request, uid=None):
    """ get topics
    """
    items = get_items("Topic", request, uid=uid, endpoint="topics")
    return {
        "url": url_for("topics"),
        "count": len(items),
        "items": items,
    }


# CREATE
@add_plone_route("/topics/create", "topics_create", methods=["POST"])
@add_plone_route("/topics/create/<string:uid>", "topics_create", methods=["POST"])
def create(context, request, uid=None):
    """ create topics
    """
    items = create_items("Topic", request, uid=uid, endpoint="topics")
    return {
        "url": url_for("topics_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/topics/update", "topics_update", methods=["POST"])
@add_plone_route("/topics/update/<string:uid>", "topics_update", methods=["POST"])
def update(context, request, uid=None):
    """ update topics
    """
    items = update_items("Topic", request, uid=uid, endpoint="topics")
    return {
        "url": url_for("topics_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/topics/delete", "topics_delete", methods=["POST"])
@add_plone_route("/topics/delete/<string:uid>", "topics_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete topics
    """
    items = delete_items("Topic", request, uid=uid, endpoint="topics")
    return {
        "url": url_for("topics_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
