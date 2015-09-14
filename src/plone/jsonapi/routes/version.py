# -*- coding: utf-8 -*-

import pkg_resources
from plone.jsonapi.routes import api
from plone.jsonapi.routes import add_plone_route

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


def version():
    dist = pkg_resources.get_distribution("plone.jsonapi.routes")
    return dist.version

__version__ = version()
__build__ = 460
__date__ = '2015-09-14'


@add_plone_route("/version", "ploneapiversion", methods=["GET"])
def apiversion(context, request):
    """ get the current version of this package
    """
    return {
        "url":     api.url_for("ploneapiversion"),
        "version": __version__,
        "build":   __build__,
        "date":    __date__,
    }
