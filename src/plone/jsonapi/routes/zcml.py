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


def configDirective(_context, register_api_routes=True):
    import plone.jsonapi.routes
    plone.jsonapi.routes.REGISTER_API_ROUTES = register_api_routes
