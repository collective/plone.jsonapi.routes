# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@nexiles.com>'
__docformat__ = 'plaintext'

import pkg_resources
from plone.jsonapi.routes import api
from plone.jsonapi.routes import add_plone_route

def version():
    dist = pkg_resources.get_distribution("plone.jsonapi.routes")
    return dist.version

__version__ = version()
__build__ = 50
__date__ = '2014-01-23'


@add_plone_route("/version", "ploneapiversion", methods=["GET"])
def apiversion(context, request):
    return {
        "url":     api.url_for("ploneapiversion"),
        "version": __version__,
        "build":   __build__,
        "date":    __date__,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
