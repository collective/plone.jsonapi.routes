# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger("plone.jsonapi.routes")


def initialize(context):
    """ Initializer called when used as a Zope 2 product.
    """
    logger.info("*** Plone JSON API ROUTES INITIALIZE ***")

# vim: set ft=python ts=4 sw=4 expandtab :
