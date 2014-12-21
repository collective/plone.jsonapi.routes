# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

# CRUD
from plone.jsonapi.routes.api import get_batched


@add_plone_route("/search", "search", methods=["GET"])
def get(context, request):
    """ search all contents
    """
    return get_batched([])

# vim: set ft=python ts=4 sw=4 expandtab :
