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
from plone.jsonapi.routes.request import get_request_data

from plone.jsonapi.routes.interfaces import IInfo

from plone.jsonapi.routes import underscore as _

logger = logging.getLogger("plone.jsonapi.routes")


#-----------------------------------------------------------------------------
#   Json API Functions
#-----------------------------------------------------------------------------

# GET
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


# CREATE
def create_items(portal_type, request, uid=None, endpoint=None):
    """ create items

    1. If the uid is given, get the object and create the content in there
       (assumed that it is folderish)
    2. If no uid is given, the target folder is the portal.
    """

    items = []

    dest = get_portal()

    if uid:
        dest = get_object_by_uid(uid)

    records = get_request_data(request)

    for record in records:
        obj = create_object_in_container(dest, portal_type, record)
        result = {
            "id": obj.getId(),
            "api_url": url_for(endpoint, uid=get_uid(obj)),
        }
        items.append(result)

    return items


# UPDATE
def update_items(portal_type, request, uid=None, endpoint=None):
    """ update items

    1. If the uid is given, the user wants to update the object with the data
       given in request body
    2. If no uid is given, the user wants to update a bunch of objects.
    """
    items = []

    payload = get_request_data(request)

    records = []
    if uid:
        records.append(get_object_by_uid(uid))
    else:
        records = (map(get_object_by_uid, _.pluck(payload, "uid")))

    for record in records:
        changeset = filter(lambda d: get_uid(record) == d.get("uid"), payload)
        data = changeset and changeset[0] or {}
        obj = update_object_with_data(record, _.omit(data, "uid"))
        result = {
            "id": obj.getId(),
            "api_url": url_for(endpoint, uid=get_uid(obj)),
        }
        items.append(result)

    return items


# DELETE
def delete_items(portal_type, request, uid=None, endpoint=None):
    """ delete items

    1. If the uid is given, we can ignore the request body and delete the
       object with the given uid (if the uid was valid).
    2. If no uid is given, the user wants to delete more than one item.
       => go through each item and extract the uid. Delete it afterwards.
       // we should do this kind of transaction base. So if we can not get an
       // object for an uid, no item will be deleted.
    3. we could check if the portal_type matches, just to be sure the user
       wants to delete the right content.
    """
    records = []
    items = []

    if uid:
        records.append(get_object_by_uid(uid))
    else:
        payload = get_request_data(request)
        records = (map(get_object_by_uid, _.pluck(payload, "uid")))

    for record in records:
        result = {"id": record.getId()}
        result["deleted"] = ploneapi.content.delete(record) == None and True or False
        items.append(result)

    return items


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

def get_portal():
    """ return the Plone site """
    return ploneapi.portal.getSite()

def get_tool(name):
    """ return a Plone tool by name """
    return ploneapi.portal.get_tool(name)

def get_portal_catalog():
    """ return portal_catalog tool """
    return get_tool("portal_catalog")

def get_portal_reference_catalog():
    """ return reference_catalog tool """
    return get_tool("reference_catalog")

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

def get_object_by_uid(uid):
    """ return the object by uid
    """
    if _.falsy(uid):
        raise RuntimeError("No UID given")

    rc  = get_portal_reference_catalog()
    obj = rc.lookupObject(uid)

    if obj is None:
        raise KeyError("No Objects for for UID %s" % uid)

    return obj

def create_object_in_container(container, portal_type, data):
    """ creates an object with the given data in the container
    """
    from AccessControl import Unauthorized
    try:
        return ploneapi.content.create(
                container=container, type=portal_type, save_id=False, **data)
    except Unauthorized:
        raise RuntimeError("You are not allowed to create this content")

def update_object_with_data(content, data):
    """ update the content with the values from data
    """

    from zope.event import notify
    from zope.lifecycleevent import ObjectModifiedEvent

    for k, v in data.items():
        field = content.getField(k)
        if field is None:
            raise KeyError("No such field '%s'" % k)
        field.set(content, v)

    notify(ObjectModifiedEvent(content))
    content.reindexObject()
    return content

# vim: set ft=python ts=4 sw=4 expandtab :
