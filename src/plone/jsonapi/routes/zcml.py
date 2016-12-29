# -*- coding: utf-8 -*-

import logging
from zope.interface import Interface
from zope.schema import Bool

logger = logging.getLogger("plone.jsonapi.routes.zcml")


class IConfig(Interface):
    """ Plone JSONAPI Config Interface
    """

    register_api_routes = Bool(
        title=u"Register Plone JSON Routes",
        description=u"""Register JSON API Routes for Plone
        """,
        required=False)

    use_advanced_query = Bool(
        title=u"Search uses Advanced Query",
        description=u"""
        Use Advanced Query if installed for catalog searches
        """,
        required=False)


def configDirective(_context, register_api_routes=True, use_advanced_query=False):

    if use_advanced_query:
        from plone.jsonapi.routes import query
        logger.info("*** USE ADVANCED QUERY ***")
        query.USE_ADVANCED_QUERY = use_advanced_query

    import plone.jsonapi.routes
    plone.jsonapi.routes.REGISTER_API_ROUTES = register_api_routes
