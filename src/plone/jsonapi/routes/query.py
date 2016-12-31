# -*- coding: utf-8 -*-

import types
import logging

from plone import api as ploneapi
from ZPublisher import HTTPRequest

from DateTime import DateTime

from plone.jsonapi.routes import request as req
from plone.jsonapi.routes import underscore as _

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


__all__ = ['search']


logger = logging.getLogger("plone.jsonapi.routes.query")


# -----------------------------------------------------------------------------
#   Public API
# -----------------------------------------------------------------------------

def search(**kw):
    """Execute a catalog search
    """

    # Fetch the right catalog
    catalog = get_catalog(**kw)

    # Make a catalog query suitable for the catalog
    query = make_query(catalog, **kw)

    return catalog(query)


# -----------------------------------------------------------------------------
#   Query Builders
# -----------------------------------------------------------------------------

def get_catalog(**kw):
    """Get the right catalog for the query.
    """
    catalog = None

    portal_type = kw.get("portal_type")
    archetype_tool = get_tool("archetype_tool")

    if portal_type and archetype_tool is not None:
        catalogs = archetype_tool.getCatalogsByType(portal_type)
        catalog = _.first(catalogs)
    else:
        catalog = get_tool("portal_catalog")

    return catalog


def make_query(catalog, **kw):
    """Generate a query for the given catalog
    """

    # build a query from the request parameters and the keywords
    query = {}

    # note: order is important!
    query.update(get_request_query(catalog))
    query.update(get_custom_query(catalog))
    query.update(get_keyword_query(catalog, **kw))

    sort_on, sort_order = get_sort_spec(catalog)
    query.update(dict(sort_order=sort_order, sort_on=sort_on))

    logger.info("make_query:: query=%s --> catalog=%s" % (query, catalog.__name__))

    return query


def get_request_query(catalog):
    """ checks the request for known catalog indexes.
    """
    query = {}

    # only known indexes get observed
    indexes = get_catalog_indexes(catalog)

    # check what we can use from the reqeust
    request = req.get_request()

    for idx in indexes:
        val = request.form.get(idx)
        if val:
            query[idx] = to_index_value(catalog, val, idx)

    return query


def get_custom_query(catalog):
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


def get_keyword_query(catalog, **kw):
    """ generates a query from the given keywords
    """
    query = dict()

    # only known indexes get observed
    indexes = get_catalog_indexes(catalog)

    for k, v in kw.iteritems():
        # handle uid
        if k.lower() == "uid":
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


# -----------------------------------------------------------------------------
#   Functional Helpers
# -----------------------------------------------------------------------------

def get_tool(name):
    try:
        return ploneapi.portal.get_tool(name)
    except ploneapi.exc.InvalidParameterError:
        return None


def calculate_delta_date(literal):
    """ calculate the date in the past from the given literal
    """
    mapping = {
        "today": 0,
        "yesterday": 1,
        "this-week": 7,
        "this-month": 30,
        "this-year": 365,
    }
    today = DateTime(DateTime().Date())  # current date without the time
    return today - mapping.get(literal, 0)


# -----------------------------------------------------------------------------
#   Catalog Helpers
# -----------------------------------------------------------------------------

def get_catalog_indexes(catalog):
    """ return the list of indexes of the portal catalog
    """
    return catalog.indexes()


def get_index(catalog, name):
    """ get the index object by name
    """
    index = catalog._catalog.getIndex(name)
    logger.info("get_index=%s of catalog '%s' --> %s" % (name, catalog.__name__, index))
    return index


def to_index_value(catalog, value, index):
    """Convert the value for a given index
    """

    # ZPublisher records can be passed to the catalog as is.
    if isinstance(value, HTTPRequest.record):
        return value

    if type(index) in types.StringTypes:
        index = get_index(catalog, index)

    if index.meta_type == "DateIndex":
        return DateTime(value)
    if index.meta_type == "BooleanIndex":
        return bool(value)
    if index.meta_type == "KeywordIndex":
        return value.split(",")

    return value


def get_sort_spec(catalog):
    """Build sort specification
    """
    all_indexes = get_catalog_indexes(catalog)
    si = req.get_sort_on(allowed_indexes=all_indexes)
    so = req.get_sort_order()
    return si, so
