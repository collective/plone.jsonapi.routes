# -*- coding: utf-8 -*-

import types
import logging

from plone.jsonapi.routes.api import url_for

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

logger = logging.getLogger("plone.jsonapi.routes")


def returns_plone_items_for(endpoint):
    """ returns a dictionary with items
    """

    def decorator(func):
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            if type(result) is types.ListType:
                return {
                    "url": url_for(endpoint),
                    "count": len(result),
                    "items": result,
                }
            return result
        return inner
    return decorator
