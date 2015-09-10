# -*- coding: utf-8 -*-

import logging
from zope.interface import Interface
from zope.schema import Bool

logger = logging.getLogger("plone.jsonapi.routes.zcml")


class IConfig(Interface):
    """ Plone JSONAPI Config Interface
    """

    use_advanced_query = Bool(
        title=u"Search uses Advanced Query",
        description=u"""
        Use Advanced Query if installed for catalog searches
        """,
        required=False)


def configDirective(_context, use_advanced_query=False):

    if use_advanced_query:
        from plone.jsonapi.routes import query
        logger.info("*** USE ADVANCED QUERY ***")
        query.USE_ADVANCED_QUERY = use_advanced_query
