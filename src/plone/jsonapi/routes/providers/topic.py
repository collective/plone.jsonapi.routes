# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/topics", "topics", methods=["GET"])
@route("/topics/<string:uid>", "topics", methods=["GET"])
def get(context, request, uid=None):
    """ get topics
    """
    return get_batched("Topic", uid=uid, endpoint="topics")


# CREATE
@route("/topics/create", "topics_create", methods=["POST"])
@route("/topics/create/<string:uid>", "topics_create", methods=["POST"])
def create(context, request, uid=None):
    """ create topics
    """
    items = create_items("Topic", uid=uid, endpoint="topics")
    return {
        "url": url_for("topics_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/topics/update", "topics_update", methods=["POST"])
@route("/topics/update/<string:uid>", "topics_update", methods=["POST"])
def update(context, request, uid=None):
    """ update topics
    """
    items = update_items("Topic", uid=uid, endpoint="topics")
    return {
        "url": url_for("topics_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/topics/delete", "topics_delete", methods=["POST"])
@route("/topics/delete/<string:uid>", "topics_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete topics
    """
    items = delete_items("Topic", uid=uid, endpoint="topics")
    return {
        "url": url_for("topics_delete"),
        "count": len(items),
        "items": items,
    }
