# -*- coding: utf-8 -*-

import logging

from plone import api as ploneapi
from plone.jsonapi.core import router

from Products.ZCatalog.interfaces import ICatalogBrain

# request helpers
from plone.jsonapi.routes.request import get_sort_limit
from plone.jsonapi.routes.request import get_sort_on
from plone.jsonapi.routes.request import get_sort_order
from plone.jsonapi.routes.request import get_query
from plone.jsonapi.routes.request import get_creator

from plone.jsonapi.routes.interfaces import IInfo

from plone.jsonapi.routes import underscore as _

logger = logging.getLogger("plone.jsonapi.routes")


#-----------------------------------------------------------------------------
#   Json API Functions
#-----------------------------------------------------------------------------

def get_items(portal_type, request, uid=None, endpoint=None):
    """ returns a list of items
    """
    # contains the full query with params
    query = make_query(request, portal_type=portal_type)
    if uid: query["UID"] = uid
    results = search(request, **query)

    # if the uid is given, get the complete information set
    complete = _.truthy(uid)
    return make_items_for(results, endpoint, complete=complete)


def make_items_for(brains, endpoint, complete=False):
    """ return a list of info dicts
    """
    def _block(brain):
        info = dict(api_url=url_for(endpoint, uid=get_uid(brain)))
        info.update(IInfo(brain)()) # call/update with the catalog brain adapter
        if complete:
            obj = brain.getObject()
            info.update(IInfo(obj)()) # call/update with the object adapter
        return info
    return map(_block, brains)

#-----------------------------------------------------------------------------
#   Portal Catalog Helper
#-----------------------------------------------------------------------------

def get_tool(name):
    """ return a Plone tool by name """
    return ploneapi.portal.get_tool(name)

def get_portal_catalog():
    """ return portal_catalog tool """
    return get_tool("portal_catalog")

def search(*args, **kw):
    """ search the portal catalog """
    pc = get_portal_catalog()
    return pc(*args, **kw)

def make_query(request, **kw):
    """ generates a content type query suitable for the portal catalog
    """

    # build the catalog query
    query = {
        "sort_limit":     get_sort_limit(request),
        "sort_on":        get_sort_on(request),
        "sort_order":     get_sort_order(request),
        "SearchableText": get_query(request),
    }

    # inject keyword args
    query.update(kw)

    # inject the creator if given
    if get_creator(request):
        query["Creator"] = get_creator(request)

    logger.info("Catalog Query --> %r", query)
    return query

#-----------------------------------------------------------------------------
#   Helper Functions
#-----------------------------------------------------------------------------

def url_for(endpoint, **values):
    """ returns the api url
    """
    return router.url_for(endpoint, force_external=True, values=values)

def get_uid(obj):
    """ get the UID of the brain/object
    """
    if ICatalogBrain.providedBy(obj):
        return obj.UID
    return obj.UID()

# vim: set ft=python ts=4 sw=4 expandtab :
