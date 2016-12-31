# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route as route

# CRUD
from plone.jsonapi.routes.api import get_batched


@route("/search", "plone.jsonapi.routes.search", methods=["GET"])
def get(context, request):
    """ search all contents
    """
    return get_batched()
