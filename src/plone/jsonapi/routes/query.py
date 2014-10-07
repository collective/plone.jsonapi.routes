# -*- coding: utf-8 -*-
#
# Copyright (c) Nexiles GmbH

import logging

from plone import api

from plone.jsonapi.routes.request import get_path
from plone.jsonapi.routes.request import get_depth
from plone.jsonapi.routes.request import get_query
from plone.jsonapi.routes.request import get_sort_on
from plone.jsonapi.routes.request import get_sort_limit
from plone.jsonapi.routes.request import get_sort_order

HAS_ADVANCED_QUERY = True
try:
    from Products import AdvancedQuery
    AQ = AdvancedQuery
except ImportError:
    HAS_ADVANCED_QUERY = False

logger = logging.getLogger("plone.jsonapi.routes.query")


def make_query(request, **kw):
    """ generates a catalog query
    """

    if HAS_ADVANCED_QUERY:
        logger.debug("AdvancedQuery installed: We could do magic here ...")
        #return make_advanced_query(request, **kw)

    logger.debug("Building standard query")
    return make_standard_query(request, **kw)


def make_standard_query(request, **kw):
    """ generates a query for the portal catalog
    """
    # build a default query from the request parameters and the keywords
    query = build_query(request, **kw)
    logger.info("Catalog Query --> %r", query)
    return query


def make_advanced_query(request, **kw):
    """ generates an advaced query
    """
    raise NotImplementedError("Usage of AdvancedQuery is not supported yet")


#-----------------------------------------------------------------------------
#   Standard Query Builders
#-----------------------------------------------------------------------------

def build_query(request, **kw):
    """ build a query spec suitable for the portal_catalog tool
    """

    # XXX we need a better way to extract all possible search variants from
    #     the request...

    query = dict()

    # check what we can use from the reqeust
    for idx in get_catalog_indexes():
        val = request.form.get(idx)
        if val: query[idx] = val

    # build a default catalog query
    query.update({
        "sort_limit":      get_sort_limit(request),
        "sort_on":         get_sort_on(request),
        "sort_order":      get_sort_order(request),
        "SearchableText":  get_query(request),
    })

    # special handling for the physical path
    path = get_path(request)
    if path:
        depth = get_depth(request)
        query["path"] = dict(query=path, depth=depth)

    # update the query with the given keywords
    update_query_with_kw(query, **kw)

    return query


def update_query_with_kw(query, **kw):
    """ add the keyword parameters to the query
    """
    indexes = get_catalog_indexes()
    # handle keywords
    for k, v in kw.iteritems():
        # handle uid
        if k.lower() == "uid":
            if v: query["UID"] = v
            continue
        # and the rest
        if k not in indexes:
            logger.warn("Skipping unknown keyword parameter '%s=%s'" % (k, v))
            continue
        logger.info("Adding '%s=%s' to query" % (k, v))
        query[k] = v

#-----------------------------------------------------------------------------
#   Catalog Helpers
#-----------------------------------------------------------------------------

def get_portal_catalog():
    """ fetch portal_catalog tool
    """
    return api.portal.get_tool("portal_catalog")


def get_catalog_indexes():
    """ return the list of indexes of the portal catalog
    """
    return get_portal_catalog().indexes()


def search(query, **kw):
    """ execute either AdvancedQuery or a StandardQuery
    """
    #if HAS_ADVANCED_QUERY and type(query) is tuple:
    #    return advanced_search(*query, **kw)
    return standard_search(query, **kw)


def standard_search(query, **kw):
    """ search the portal catalog
    """
    logger.info("Standard Query -> %r" % (query))
    pc = get_portal_catalog()
    return pc(query, **kw)


def advanced_search(query, sort_specs=()):
    """ search the portal catalog with the advanced query
    """
    logger.info("Advanced Query -> %s sort_specs=%r" % (query, sort_specs))
    pc = get_portal_catalog()
    return pc.evalAdvancedQuery(query, sort_specs)

# vim: set ft=python ts=4 sw=4 expandtab :
