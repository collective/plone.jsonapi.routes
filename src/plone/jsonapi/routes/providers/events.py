# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_items
from plone.jsonapi.routes.api import create_items
from plone.jsonapi.routes.api import update_items
from plone.jsonapi.routes.api import delete_items

from plone.jsonapi.routes.api import url_for


# GET
@add_plone_route("/events", "events", methods=["GET"])
@add_plone_route("/events/<string:uid>", "events", methods=["GET"])
def get(context, request, uid=None):
    """ get events
    """
    items = get_items("Event", request, uid=uid, endpoint="events")
    return {
        "url": url_for("events"),
        "count": len(items),
        "items": items,
    }


# CREATE
@add_plone_route("/events/create", "events_create", methods=["POST"])
@add_plone_route("/events/create/<string:uid>", "events_create", methods=["POST"])
def create(context, request, uid=None):
    """ create events
    """
    items = create_items("Event", request, uid=uid, endpoint="events")
    return {
        "url": url_for("events_create"),
        "count": len(items),
        "items": items,
    }


# UPDATE
@add_plone_route("/events/update", "events_update", methods=["POST"])
@add_plone_route("/events/update/<string:uid>", "events_update", methods=["POST"])
def update(context, request, uid=None):
    """ update events
    """
    items = update_items("Event", request, uid=uid, endpoint="events")
    return {
        "url": url_for("events_update"),
        "count": len(items),
        "items": items,
    }


# DELETE
@add_plone_route("/events/delete", "events_delete", methods=["POST"])
@add_plone_route("/events/delete/<string:uid>", "events_delete", methods=["POST"])
def delete(context, request, uid=None):
    """ delete events
    """
    items = delete_items("Event", request, uid=uid, endpoint="events")
    return {
        "url": url_for("events_delete"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
