# -*- coding: utf-8 -*-

from plone.jsonapi.routes import api
from plone.jsonapi.routes import add_plone_route

from plone.jsonapi.routes.version import __version__
from plone.jsonapi.routes.version import __build__
from plone.jsonapi.routes.version import __date__


@add_plone_route("/version", "plone.jsonapi.routes.version", methods=["GET"])
def apiversion(context, request):
    """ get the current version of this package
    """
    return {
        "url":     api.url_for("plone.jsonapi.routes.version"),
        "version": __version__,
        "build":   __build__,
        "date":    __date__,
    }
