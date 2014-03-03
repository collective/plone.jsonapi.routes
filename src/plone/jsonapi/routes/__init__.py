# -*- coding: utf-8 -*-

import re
import logging

from plone.jsonapi.core.browser.router import add_route
from plone.jsonapi.core.browser.router import DefaultRouter

from api import url_for

BASE_URL = "/plone/api/1.0"

logger = logging.getLogger("plone.jsonapi.routes")


def add_plone_route(rule, endpoint=None, **kw):
    """ add a Plone JSON API route
    """
    def apiurl(rule):
         return '/'.join(s.strip('/') for s in ["", BASE_URL, rule])

    def wrapper(f):
        try:
            DefaultRouter.add_url_rule(apiurl(rule), endpoint=endpoint, view_func=f, options=kw)
        except AssertionError:
            pass
        return f

    return wrapper


def get_api_routes_for(segment):
    """ return a list of all routes registered for the given url segment
    """
    adapter = DefaultRouter.get_adapter()

    out = []
    rx = re.compile(r".*%s/[\w]+$" % segment)

    for rule in adapter.map.iter_rules():
        if rx.match(rule.rule):
            endpoint = rule.endpoint
            info = DefaultRouter.view_functions.get(endpoint).__doc__
            url  = DefaultRouter.url_for(endpoint, force_external=True)
            out.append({
                "url":  url,
                "info": info and info.strip() or "No description available",
                "methods": ",".join(rule.methods),
            })
    return out


@add_route(BASE_URL, "api", methods=["GET"])
@add_plone_route("api.json", "api", methods=["GET"])
def api_json(context, request):
    """ API URLs
    """
    items = get_api_routes_for(BASE_URL)

    return {
        "url": DefaultRouter.url_for("api", force_external=True),
        "count": len(items),
        "items": items,
    }


def initialize(context):
    """ Initializer called when used as a Zope 2 product.
    """
    logger.info("*** PLONE.JSONAPI.ROUTES INITIALIZE ***")

    # We have to import the modules so that the routes get initialized
    import pkgutil
    import providers

    prefix = providers.__name__ + "."
    for importer, modname, ispkg in pkgutil.iter_modules(providers.__path__, prefix):
        module = __import__(modname, fromlist="dummy")
        logger.info("INITIALIZED ROUTE PROVIDER ---> %s" % module.__name__)

    import version
    logger.info("INITIALIZED ROUTE PROVIDER ---> %s" % version.__name__)

# vim: set ft=python ts=4 sw=4 expandtab :
