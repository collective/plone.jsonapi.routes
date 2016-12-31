# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@route("/events", "plone.jsonapi.routes.events", methods=["GET"])
@route("/events/<string:uid>", "plone.jsonapi.routes.events", methods=["GET"])
def get(context, request, uid=None):
    """ get events
    """
    return get_batched("Event", uid=uid, endpoint="plone.jsonapi.routes.events")


# CREATE
@route("/events/create", "plone.jsonapi.routes.events_create", methods=["POST"])
@route("/events/create/<string:uid>", "plone.jsonapi.routes.events_create", methods=["POST"])
def create(context, request, uid=None):
    """ create events
    """
    items = create_items("Event", uid=uid, endpoint="plone.jsonapi.routes.events")
    return {
        "url": url_for("plone.jsonapi.routes.events_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@route("/events/update", "plone.jsonapi.routes.events_update", methods=["POST"])
@route("/events/update/<string:uid>", "plone.jsonapi.routes.events_update", methods=["POST"])
def update(context, request, uid=None):
    """ update events
    """
    items = update_items("Event", uid=uid, endpoint="plone.jsonapi.routes.events")
    return {
        "url": url_for("plone.jsonapi.routes.events_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@route("/events/delete", "plone.jsonapi.routes.events_delete", methods=["POST"])
@route("/events/delete/<string:uid>", "plone.jsonapi.routes.events_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete events
    """
    items = delete_items("Event", uid=uid, endpoint="plone.jsonapi.routes.events")
    return {
        "url": url_for("plone.jsonapi.routes.events_delete"),
        "count": len(items),
        "items": items,
    }
