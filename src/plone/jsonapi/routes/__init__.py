# -*- coding: utf-8 -*-
import logging
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


# API JSON
@add_plone_route("/api.json", "api_json", methods=["GET"])
def api_json(context, request, uid=None):
    """ get the api
    """
    items = []
    for rule in DefaultRouter.url_map.iter_rules():
        if rule.rule.startswith(BASE_URL):
            items.append({
                "endpoint": rule.endpoint,
                "url":      url_for(rule.endpoint),
                "methods":  list(rule.methods),
                "arguments": list(rule.arguments),
            })

    return {
        "url": url_for("api_json"),
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
        logger.info("INITIALIZED ROUTE PROVIDER [%s]" % module.__name__)

    import version
    logger.info("INITIALIZED ROUTE PROVIDER [%s]" % version.__name__)

# vim: set ft=python ts=4 sw=4 expandtab :
