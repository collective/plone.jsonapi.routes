# -*- coding: utf-8 -*-

import types
import logging
import pkg_resources

from plone import api
from ZPublisher import HTTPRequest

from DateTime import DateTime

from plone.jsonapi.routes import request as req
from plone.jsonapi.routes import underscore as _

try:
    pkg_resources.get_distribution('Products.AdvancedQuery')
    from Products.AdvancedQuery import Eq
    from Products.AdvancedQuery import In
    from Products.AdvancedQuery import Generic
except pkg_resources.DistributionNotFound:
    HAS_ADVANCED_QUERY = False
else:
    HAS_ADVANCED_QUERY = True

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


__all__ = ['search', 'make_query']


logger = logging.getLogger("plone.jsonapi.routes.query")

# TODO: make this an configurable option -- maybe zcml?
#       or Environment Variable?
USE_ADVANCED_QUERY = False


# -----------------------------------------------------------------------------
#   Public API
# -----------------------------------------------------------------------------

def search(query, **kw):
    """ execute either AdvancedQuery or a StandardQuery
    """
    if USE_ADVANCED_QUERY and HAS_ADVANCED_QUERY and type(query) is tuple:
        return advanced_search(*query, **kw)
    return standard_search(query, **kw)


def make_query(**kw):
    """ generates a catalog query
    """
    if USE_ADVANCED_QUERY and HAS_ADVANCED_QUERY:
        return make_advanced_query(**kw)
    return make_standard_query(**kw)


# -----------------------------------------------------------------------------
#   Query Builders
# -----------------------------------------------------------------------------

def make_standard_query(**kw):
    """ generates a query for the portal catalog
    """
    logger.info("Building **standard** query")

    # build a default query from the request parameters and the keywords
    query = build_catalog_query(**kw)

    sort_on, sort_order = get_sort_spec()
    query.update(dict(sort_order=sort_order, sort_on=sort_on))

    return query


def make_advanced_query(**kw):
    """ generates a query suitable for the portal catalog
    """
    logger.info("Building **advanced** query")

    # build the initial query
    query = build_catalog_query(**kw)

    # transform to advanced query
    advanced_query = to_advanced_query(query)

    # get the sort specification
    sort = get_sort_spec()

    return advanced_query, (sort, )


def build_catalog_query(**kw):
    """ build an initial query object

    this query can be used directly for a std. catalog query
    """
    query = {}

    # note: order is important!
    query.update(get_request_query())
    query.update(get_custom_query())
    query.update(get_keyword_query(**kw))

    logger.info("build_catalog_query::query=%s" % query)
    return query


def get_request_query():
    """ checks the request for known catalog indexes.
    """
    query = {}

    # only known indexes get observed
    indexes = get_catalog_indexes()

    # check what we can use from the reqeust
    request = req.get_request()

    for idx in indexes:
        val = request.form.get(idx)
        if val:
            query[idx] = to_index_value(val, idx)

    return query


def get_custom_query():
    """ checks the request for custom query keys.
    """
    query = {}

    # searchable text queries
    q = req.get_query()
    if q:
        query["SearchableText"] = q

    # physical path queries
    path = req.get_path()
    if path:
        query["path"] = {'query': path, 'depth': req.get_depth()}

    # special handling for recent created/modified
    recent_created = req.get_recent_created()
    if recent_created:
        date = calculate_delta_date(recent_created)
        query["created"] = {'query': date, 'range': 'min'}

    recent_modified = req.get_recent_modified()
    if recent_modified:
        date = calculate_delta_date(recent_modified)
        query["modified"] = {'query': date, 'range': 'min'}

    return query


def get_keyword_query(**kw):
    """ generates a query from the given keywords
    """
    query = dict()

    # only known indexes get observed
    indexes = get_catalog_indexes()

    for k, v in kw.iteritems():
        # handle uid
        if v and k.lower() == "uid":
            if v:
                query["UID"] = v
            continue
        # handle portal_type
        if k.lower() == "portal_type":
            if v:
                query["portal_type"] = _.to_list(v)
            continue
        # and the rest
        if k not in indexes:
            logger.warn("Skipping unknown keyword parameter '%s=%s'" % (k, v))
            continue
        if v is None:
            logger.warn("Skip value 'None' in kw parameter '%s=%s'" % (k, v))
            continue
        logger.info("Adding '%s=%s' to query" % (k, v))
        query[k] = v

    return query


def to_advanced_query(query):
    """ convert a dictionary to an advanced query
    """

    # nothing to do
    if not query:
        return Eq("Title", "")

    a_query = None

    def get_query_expression_for(value):
        # return the Advanced Query Expression
        if type(value) in (tuple, list):
            return In
        if type(value) is dict:
            return Generic
        return Eq

    for k, v in query.iteritems():
        exp = get_query_expression_for(v)
        # first loop, build the initial query expression
        if a_query is None:
            a_query = exp(k, v)
        else:
            a_query = a_query & exp(k, v)

    return a_query


# -----------------------------------------------------------------------------
#   Functional Helpers
# -----------------------------------------------------------------------------

def calculate_delta_date(literal):
    """ calculate the date in the past from the given literal
    """
    mapping = {
        "today":      0,
        "yesterday":  1,
        "this-week":  7,
        "this-month": 30,
        "this-year":  365,
    }
    today = DateTime(DateTime().Date())  # current date without the time
    return today - mapping.get(literal, 0)


# -----------------------------------------------------------------------------
#   Catalog Helpers
# -----------------------------------------------------------------------------

def get_portal_catalog():
    """ fetch portal_catalog tool
    """
    return api.portal.get_tool("portal_catalog")


def get_catalog_indexes():
    """ return the list of indexes of the portal catalog
    """
    return get_portal_catalog().indexes()


def get_index(name):
    """ get the index object by name
    """
    return get_portal_catalog()._catalog.getIndex(name)


def to_index_value(value, index):
    """ convert the value for the given index
    """
    # ZPublisher records can be passed to the catalog as is.
    if isinstance(value, HTTPRequest.record):
        return value

    if type(index) in types.StringTypes:
        index = get_index(index)

    if index.meta_type == "DateIndex":
        return DateTime(value)
    if index.meta_type == "BooleanIndex":
        return bool(value)
    if index.meta_type == "KeywordIndex":
        return value.split(",")

    return value


def get_sort_spec():
    """ build sort specification
    """
    all_indexes = get_portal_catalog().indexes()
    si = req.get_sort_on(allowed_indexes=all_indexes)
    so = req.get_sort_order()
    return si, so


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
