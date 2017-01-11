# -*- coding: utf-8 -*-

import re
import logging

from plone.jsonapi.core.browser.router import add_route
from plone.jsonapi.core.browser.router import DefaultRouter

__author__ = 'Ramon Bartl <rb@ridingbytes.com>'
__docformat__ = 'plaintext'


BASE_URL = "/plone/api/1.0"
REGISTER_API_ROUTES = True

logger = logging.getLogger("plone.jsonapi.routes")


def add_plone_route(rule, endpoint=None, **kw):
    """ add a Plone JSON API route
    """
    def apiurl(rule):
        return '/'.join(s.strip('/') for s in ["", BASE_URL, rule])

    def wrapper(f):
        try:
            DefaultRouter.add_url_rule(apiurl(rule),
                                       endpoint=endpoint,
                                       view_func=f,
                                       options=kw)
        except AssertionError:
            pass
        return f

    return wrapper


def get_api_routes_for(segment):
    """ return a list of all routes registered for the given url segment
    """
    adapter = DefaultRouter.get_adapter()

    endpoints = set()
    rx = re.compile(r".*%s/[\w]" % segment)

    for rule in adapter.map.iter_rules():
        if rx.match(rule.rule):
            endpoints.add(rule.endpoint)

    out = []
    for endpoint in endpoints:
        info = DefaultRouter.view_functions.get(endpoint).__doc__
        url = DefaultRouter.url_for(endpoint, force_external=True)
        out.append({
            "url":  url,
            "info": info and info.strip() or "No description available",
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

    if not REGISTER_API_ROUTES:
        logger.info("*** ROUTE INITIALIZATION DEACTIVATED VIA ZCML ***")
        from providers import get
        logger.info("*** ADDED DEFAULT ROUTE PROVIDER --> %s ***" % get.__name__)
        return

    # We have to import the modules so that the routes get initialized
    import pkgutil
    import providers

    prefix = providers.__name__ + "."
    for importer, modname, ispkg in pkgutil.iter_modules(
            providers.__path__, prefix):
        module = __import__(modname, fromlist="dummy")
        logger.info("INITIALIZED ROUTE PROVIDER ---> %s" % module.__name__)
