# -*- coding: utf-8 -*-

import logging

from plone import api as ploneapi
from plone.jsonapi.core import router

# request helpers
from plone.jsonapi.routes.request import get_sort_limit
from plone.jsonapi.routes.request import get_sort_on
from plone.jsonapi.routes.request import get_sort_order
from plone.jsonapi.routes.request import get_query
from plone.jsonapi.routes.request import get_creator

logger = logging.getLogger("plone.jsonapi.routes")

#-----------------------------------------------------------------------------
# OBJECT INFO
#-----------------------------------------------------------------------------

def get_items(portal_type, request, uid=None, endpoint=None):
    """ returns a list of items
    """
    # contains the full query with params
    query = make_query(request, portal_type=portal_type)
    if uid: query["UID"] = uid
    results = search(request, **query)

    # if the uid is given, get the complete information set
    complete = uid and True or False
    return make_items_for(results, endpoint, complete=complete)

def make_items_for(brains, endpoint, complete=False):
    """ return a list of info dicts
    """
    def _block(brain):
        base = get_base_info(brain, endpoint)
        if complete:
            base.update(get_complete_info(brain, endpoint))
        return base
    return map(_block, brains)

def get_base_info(brain, endpoint):
    """ returns the base information for the given object
    """
    logger.info("get_base_info:: -> get base info for %s" % brain.getId)
    return {
        "id":      brain.getId,
        "uid":     brain.UID,
        "url":     brain.getURL(),
        "title":   brain.Title,
        "api_url": url_for(endpoint, uid=brain.UID),
    }

def get_complete_info(brain, endpoint=None):
    """ wake up the object and get the full info
    """
    logger.info("get_complete_info:: -> get object info for: %s" % brain.getId)
    obj = brain.getObject()

    return {
        "created":   obj.created().ISO8601(),
        "modified":  obj.modified().ISO8601(),
        "effective": obj.effective().ISO8601(),
    }

def url_for(endpoint, **values):
    """ returns the api url
    """
    return router.url_for(endpoint, force_external=True, values=values)

#-----------------------------------------------------------------------------
# CATALOG
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

# vim: set ft=python ts=4 sw=4 expandtab :
