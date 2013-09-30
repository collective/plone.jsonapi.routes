# -*- coding: utf-8 -*-

import json
import logging
import dateutil
import datetime

from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from plone import api as ploneapi
from plone.jsonapi import router

from Acquisition import aq_parent, aq_inner

logger = logging.getLogger("collective.jsonapi.routes.api")


# endpoint mappings for the different content types
resources = {
    " Products.ATContentTypes.interfaces.document.IATDocument": "documents",
}

#-----------------------------------------------------------------------------
# REQUEST HELPERS
#-----------------------------------------------------------------------------

def get_sort_limit(request):
    """ returns the 'sort_limit' from the request
    """
    limit = request.form.get("limit")

    if limit is None or not limit.isdigit():
        return None
    return int(limit)

def get_start(request):
    """ returns the 'start' from the request
    """
    start = request.form.get("start")

    if start is None or not start.isdigit():
        return None
    return int(start)

def get_sort_on(request):
    """ returns the 'sort_on' from the request
    """
    sort_on = request.form.get("sort_on")

    if sort_on in get_portal_catalog().indexes():
        return sort_on
    return "getObjPositionInParent"

def get_sort_order(request):
    """ returns the 'sort_order' from the request
    """
    sort_order = request.form.get("sort_order")
    if sort_order in ["ascending", "a", "asc", "up", "high"]:
        return "ascending"
    if sort_order in ["descending", "d", "desc", "down", "low"]:
        return "descending"
    return "descending"

def get_query(request):
    """ returns the 'query' from the request
    """
    q = request.form.get("q", "")

    qs = q.lstrip("*.!$%&/()=#-+:'`´^")
    if qs and not qs.endswith("*"):
        qs += "*"
    return qs

def get_creator(request):
    """ returns the 'creator' from the request
    """
    return request.form.get("creator", "")

def get_request_data(request):
    """ extract and convert the json data from the request

    returns a list of dictionaries
    """

    data = json.loads(request["BODY"])

    # we want to iterate over the items in case that we get more than one
    # record.
    if type(data) not in (list, tuple):
        data = [data]
    return data

#-----------------------------------------------------------------------------
# PORTAL CATALOG HELPERS
#-----------------------------------------------------------------------------

def get_portal_catalog():
    """ return portal_catalog tool """
    return ploneapi.portal.get_tool("portal_catalog")

def search(*args, **kw):
    """ search the portal catalog """
    pc = get_portal_catalog()
    return pc(*args, **kw)

def make_query(request, **kw):
    """ generates a content type query suitable for the portal catalog
    """

    # build the catalog query
    query = {
        "sort_limit":      get_sort_limit(request),
        "sort_on":         get_sort_on(request),
        "sort_order":      get_sort_order(request),
        "SearchableText":  get_query(request),
    }

    # inject keyword args
    query.update(kw)

    # inject the creator if given
    if get_creator(request):
        query["Creator"] = get_creator(request)

    logger.info("Catalog Query --> %r", query)
    return query

def get_objects(query):
    """ returns the waked-up objects from a catalog search
    """
    brains = search(query)
    return [brain.getObject() for brain in brains]

def search_objects(request, **kw):
    """ returns a catalog search with the waked up objects
    """
    full_query = make_query(request, **kw)
    return get_objects(full_query)

def search_items(request, **kw):
    """ returns a catalog search with the waked up objects
    """
    full_query = make_query(request, **kw)
    return search(full_query)

def get_object_by_uid(uid):
    """ return the object by uid
    """
    if not uid:
        raise ValueError("No UID given")

    results = get_objects(dict(UID=uid))

    if len(results) != 1:
        raise ValueError("Found %d Objects for for UID %s" % (len(results), uid))

    return results.pop()

def get_contents(iface, request, uid=None):
    """ catalog search

    if uid is given, then the UID index is searched
    """
    # create a catalog query for the given interface
    query = dict(object_provides = iface.__identifier__)

    # inject the uid if given
    if uid: query["UID"] = uid
    return search_objects(request, **query)

#-----------------------------------------------------------------------------
# PORTAL WORKFLOW HELPERS
#-----------------------------------------------------------------------------

def get_portal_workflow():
    """ return portal_workflow tool """
    return ploneapi.portal.get_tool("portal_workflow")

def do_action_for(obj, transition):
    """ perform wf transition """
    return ploneapi.content.transition(obj, transition)

#-----------------------------------------------------------------------------
# CONTENT CREATE/UPDATE
#-----------------------------------------------------------------------------

def create_object_in_container(container, portal_type, data):
    """ creates an object with the given data in the container
    """
    logger.info("create_object_in_container: container=%r, portal_type=%r, data=%r", container, portal_type, data)

    from AccessControl import Unauthorized
    try:
        return ploneapi.content.create(container=container,
                                       type=portal_type,
                                       save_id=False,
                                        **data)
    except Unauthorized:
        raise RuntimeError("You are not allowed to create this content")

def update_object_with_data(content, data):
    """ update the content with the values from data
    """
    logger.info("update_object_with_data: content=%r, data=%r", content, data)

    for k, v in data.items():
        setattr(content, k, v)

    notify(ObjectModifiedEvent(content))
    return content

#-----------------------------------------------------------------------------
# OTHER HELPERS
#-----------------------------------------------------------------------------

def get_base_info(obj, endpoint=None):
    """ returns the base information for the given object
    """
    logger.info("get_base_info::obj='%s'", obj.getId())

    # query the endpoint by portal type
    if endpoint is None:
        endpoint = resources.get(obj.portal_type)

    return {
        "id":        obj.getId(),
        "uid":       obj.UID(),
        "title":     obj.title,
        "url":       url_for(endpoint, uid=obj.UID()),
        "plone_url": obj.absolute_url(),
    }

def get_parent_info(obj, endpoint=None):
    """ returns the infos for the parent object
    """

    parent = aq_parent(aq_inner(obj))

    if endpoint is None:
        endpoint = resources.get(parent.portal_type)

    return {
        "parent_id":  parent.getId(),
        "parent_uid":  parent.UID(),
        "parent_url": url_for(endpoint, uid=parent.UID())
    }

def get_schema_save_data(iface, data):
    """ process data according to the schema field.
    """

    values = dict()
    for k, v in data.iteritems():
        field = iface.get(k)

        logger.info("get_schema_save_data::processing key=%r, value=%r, field=%r", k, v, field)
        if field is None:
            logger.info("get_schema_save_data::skipping key=%r", k)
            continue

        values[k] = v

        # parsing dates
        if field._type == datetime.date and v:
            dt = dateutil.parser.parse(v)
            logger.info("parsing %r to datetime => %r", v, dt)
            values[k] = dt

    return values

def to_iso_date(date=None):
    """ get the iso string for python datetime objects
    """
    if date is None:
        return ""
    return date.isoformat()

def url_for(endpoint, **values):
    """ returns the api url
    """
    return router.url_for(endpoint, force_external=True, values=values)

def get_portal():
    return ploneapi.portal.getSite()

def get_current_user():
    return ploneapi.user.get_current()

def paginate(request, items):
    """ lame pagination
    """
    limit = get_sort_limit(request)
    start = get_start(request)

    if limit and start:
        return items[start:limit+start]
    elif limit:
        return items[:limit]
    return items

# vim: set ft=python ts=4 sw=4 expandtab :
