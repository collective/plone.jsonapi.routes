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

    # Support different Catalogs (e.g. like in Bika LIMS)
    #
    # The portal_type can be added as a keyword from an explicit route provider or
    # as a request parameter (multiple times) in a generic search provider.
    #
    # A keyword takes precedence over a request parameter to avoid searches like this:
    # http://localhost:8080/@@API/plone/api/1.0/folders?portal_type=Document&portal_type=Collection
    portal_types = kw.get("portal_type") or req.get("portal_type")

    # Fetch the catalog depending on the portal_type
    # N.B. The conversion to list takes care of string representations of
    #      lists, which might get returned from the batch navigation, e.g.
    #      "['Document', 'Folder']"
    catalog = get_catalog(_.first(portal_types))

    # create catalog query
    query = make_query(catalog, **kw)

    return catalog(query)


# -----------------------------------------------------------------------------
#   Query Builders
# -----------------------------------------------------------------------------

def get_catalog(portal_type=None):
    """Get the right catalog for the portal_type.
    """

    # Check if the user asked for a specific catalog to use
    catalog = get_tool(req.get("catalog"))
    if catalog is not None:
        return catalog

    # Ask the archetype_tool if it knows the right catalog for this portal_type
    archetype_tool = get_tool("archetype_tool")
    if portal_type and archetype_tool:
        # make sure we don't have a list here
        portal_type = _.first(portal_type)
        # returns a list
        catalog = archetype_tool.getCatalogsByType(portal_type)
        return _.first(catalog)

    # Return the portal_catalog tool by default
    return get_tool("portal_catalog")


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
    """Checks the request for known catalog indexes and converts the values
    to fit the type of the catalog index.

    :param catalog: The catalog to build the query for
    :type catalog: ZCatalog
    :returns: Catalog query
    :rtype: dict
    """
    query = {}

    # only known indexes get observed
    indexes = catalog.indexes()

    # check what we can use from the reqeust
    request = req.get_request()

    for index in indexes:
        # Check if the request contains a parameter named like the index
        value = request.form.get(index)
        # No value found, continue
        if value is None:
            continue
        # Convert the found value to format understandable by the index
        index_value = to_index_value(catalog, value, index)
        # Conversion returned None, continue
        if index_value is None:
            continue
        # Append the found value to the query
        query[index] = index_value

    return query


def get_custom_query(catalog):
    """Extracts custom query keys from the index.

    Parameters which get extracted from the request:

        `q`: Passes the value to the `SearchableText`
        `path`: Creates a path query
        `recent_created`: Creates a date query
        `recent_modified`: Creates a date query

    :param catalog: The catalog to build the query for
    :type catalog: ZCatalog
    :returns: Catalog query
    :rtype: dict
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
    """Generates a query from the given keywords. Only known indexes make it
    into the generated query.

    :param catalog: The catalog to build the query for
    :type catalog: ZCatalog
    :returns: Catalog query
    :rtype: dict
    """
    query = dict()

    # Only known indexes get observed
    indexes = catalog.indexes()

    # Handle additional keyword parameters
    for k, v in kw.iteritems():
        # handle uid in keywords
        if k.lower() == "uid":
            k = "UID"
        # handle portal_type in keywords
        if k.lower() == "portal_type":
            if v:
                v = _.to_list(v)
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
    if name is None:
        return None
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

    if index.id == "portal_type":
        return filter(lambda x: x, _.to_list(value))
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
    all_indexes = catalog.indexes()
    si = req.get_sort_on(allowed_indexes=all_indexes)
    so = req.get_sort_order()
    return si, so
