# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_batched

DEFAULT_TYPES = [
    "Collection",
    "Document",
    "Event",
    "File",
    "Folder",
    "Image",
    "Link",
    "News Item",
    "Topic",
]

@add_plone_route("/search", "search", methods=["GET"])
def get(context, request, uid=None):
    """ search all contents
    """

    return get_batched(DEFAULT_TYPES, request, uid=uid, endpoint="search")

# vim: set ft=python ts=4 sw=4 expandtab :
