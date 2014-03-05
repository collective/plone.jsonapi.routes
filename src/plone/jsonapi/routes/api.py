# -*- coding: utf-8 -*-

import logging

from plone import api as ploneapi
from plone.jsonapi.core import router

from Products.CMFCore.interfaces import ISiteRoot
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ATContentTypes.interfaces import IATContentType

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
#   Json API (CRUD) Functions
#-----------------------------------------------------------------------------

# GET
def get_items(portal_type, request, uid=None, endpoint=None):
    """ returns a list of items

    1. If the UID is given, fetch the object directly => should return 1 item
    2. If no UID is given, search for all items of the given portal_type
    """
    # contains the full query with params
    query = make_query(request, portal_type=portal_type)
    if uid is not None: query["UID"] = uid

    results = search(request, **query)

    # if the uid is given, get the complete information set
    complete = uid and True or False
    return make_items_for(results, endpoint, complete=complete)


### CREATE
def create_items(portal_type, request, uid=None, endpoint=None):
    """ create items

    1. If the uid is given, get the object and create the content in there
       (assumed that it is folderish)
    2. If no uid is given, the target folder is the portal.
    """

    # destination where to create the content
    dest = uid and get_object_by_uid(uid) or None

    # extract the data from the request
    records = get_request_data(request)

    results = []
    for record in records:
        if dest is None:
            # find the container for content creation
            dest = find_target_container(record, portal_type)
        obj = create_object_in_container(dest, portal_type, record)
        results.append(obj)

    return make_items_for(results, endpoint=endpoint)

### UPDATE
def update_items(portal_type, request, uid=None, endpoint=None):
    """ update items

    1. If the uid is given, the user wants to update the object with the data
       given in request body
    2. If no uid is given, the user wants to update a bunch of objects.
    """

    # the data to update
    records = get_request_data(request)

    objects = []
    if uid:
        objects.append(get_object_by_uid(uid))
    else:
        # get the objects for the given uids
        objects = (map(get_object_by_uid, _.pluck(records, "uid")))

    results = []
    for obj in objects:
        # get the update dataset for this object

        if uid:
            record = records and records[0] or {}
        else:
            # the uid is inside the payload
            record = filter(lambda d: get_uid(obj) == d.get("uid"), records)
            record = record and record[0] or {}

        # do a wf transition
        if record.get("transition", None):
            t = record.get("transition")
            logger.info(">>> Do Transition '%s' for Enquiry %s", t, obj.getId())
            do_action_for(obj, t)

        obj = update_object_with_data(obj, record)
        results.append(obj)
    return make_items_for(results, endpoint=endpoint)

### DELETE
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

    objects = []
    if uid:
        objects.append(get_object_by_uid(uid))
    else:
        payload = get_request_data(request)
        objects = (map(get_object_by_uid, _.pluck(payload, "uid")))

    results = []
    for obj in objects:
        result = {"id": obj.getId()}
        result["deleted"] = ploneapi.content.delete(obj) == None and True or False
        results.append(result)

    return results

#-----------------------------------------------------------------------------
#   Data Functions
#-----------------------------------------------------------------------------

def make_items_for(brains_or_objects, endpoint, complete=True):
    """ return a list of info dicts
    """
    def _block(brain):
        info = dict(api_url=url_for(endpoint, uid=get_uid(brain)))
        # update with std. catalog metadata
        info.update(IInfo(brain)())

        # switch to wake up the object and complete the informations with the
        # data of the content adapter
        if complete:
            obj = get_object(brain)
            info.update(IInfo(obj)())
            info.update(get_parent_info(obj))
        return info

    return map(_block, brains_or_objects)


def get_parent_info(obj):
    """ returns the infos for the parent object
    """

    parent   = get_parent(obj)
    endpoint = get_endpoint(parent.portal_type)

    if ISiteRoot.providedBy(parent):
        return {
            "parent_id":  parent.getId(),
            "parent_uid": 0
        }

    return {
        "parent_id":  parent.getId(),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, uid=get_uid(parent))
    }

def get_subcontents(parent, ptype):
    """ returns the contained contents
    """

    # get the contained objects
    children = parent.listFolderContents(
            contentFilter={"portal_type": [ptype]})

    # get the endpoint for the searched results
    endpoint = get_endpoint(ptype)

    items = []
    for child in children:
        info = dict(api_url=url_for(endpoint, uid=get_uid(child)))
        info.update(IInfo(child)())
        info.update(get_parent_info(child))
        items.append(info)

    return {
        "url":   url_for(endpoint),
        "count": len(items),
        "items": items
    }

#-----------------------------------------------------------------------------
#   Portal Catalog Helper
#-----------------------------------------------------------------------------

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

#-----------------------------------------------------------------------------
#   Functional Helpers
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

def get_portal_types_tool():
    """ return the portal types tool """
    return get_tool("portal_types")

def get_portal_workflow():
    """ return portal_workflow tool """
    return get_tool("portal_workflow")

def url_for(endpoint, **values):
    """ returns the api url
    """
    return router.url_for(endpoint, force_external=True, values=values)

def get_uid(obj):
    """ get the UID of the brain/object
    """
    if ICatalogBrain.providedBy(obj):
        return obj.UID
    if ISiteRoot.providedBy(obj):
        return "siteroot"
    return obj.UID()

def get_schema(obj):
    """ return the schema of this type """
    if IATContentType.providedBy(obj):
        return obj.schema
    pt = get_portal_types_tool()
    fti = pt.getTypeInfo(obj.portal_type)
    return fti.lookupSchema()

def get_object(brain_or_object):
    """ return the referenced object """
    if not ICatalogBrain.providedBy(brain_or_object):
        return brain_or_object
    return brain_or_object.getObject()

def get_parent(brain_or_object):
    """ return the referenced object """
    obj = get_object(brain_or_object)
    return obj.aq_parent

def get_endpoint(portal_type):
    """ get the endpoint for this type """
    # handle portal types with dots
    portal_type = portal_type.split(".").pop()
    # remove whitespaces
    portal_type = portal_type.replace(" ", "")
    # lower and pluralize
    portal_type = portal_type.lower() + "s"

    return portal_type

def get_object_by_uid(uid):
    """ return the object by uid
    """
    if not uid:
        raise RuntimeError("No UID given")

    obj = None
    pc = get_portal_catalog()
    rc = get_portal_reference_catalog()
    res = pc.search(dict(UID=uid))

    if len(res) > 1:
        raise ValueError("More than one object found for UID %s" % uid)
    elif len(res) == 0:
        # try with the ref catalog
        obj = rc.lookupObject(uid)
    else:
        obj = res[0].getObject()

    if obj is None:
        raise KeyError("No Objects found for UID %s" % uid)

    return obj

def find_target_container(record, portal_type):
    """ find the target container for this record

    """
    parent_uid = record.get("parent_uid")

    if parent_uid:
        # if we have an parent_uid, we use it
        return get_object_by_uid(parent_uid)

    if parent_uid == 0:
        return get_portal()

    raise RuntimeError("Could not find a suitable place to create the content")

def do_action_for(obj, transition):
    """ perform wf transition """
    return ploneapi.content.transition(obj, transition)

def get_current_user():
    """ return the current logged in user """
    return ploneapi.user.get_current()

def create_object_in_container(container, portal_type, record):
    """ creates an object with the given data in the container
    """
    from AccessControl import Unauthorized
    try:
        title = record.get("title")
        obj = ploneapi.content.create(
                container=container, type=portal_type, title=title, save_id=True)
        return update_object_with_data(obj, record)
    except Unauthorized:
        raise RuntimeError("You are not allowed to create this content")

def update_object_with_data(content, record):
    """ update the content with the values from records
    """
    schema = get_schema(content)
    is_atct = IATContentType.providedBy(content)

    for k, v in record.items():
        field = schema.get(k)

        logger.info("update_object_with_data::processing key=%r, value=%r, field=%r", k, v, field)
        if field is None:
            logger.info("update_object_with_data::skipping key=%r", k)
            continue

        if is_atct:
            # XXX handle security
            mutator = field.getMutator(content)
            mutator(v)
        else:
            setattr(content, k, v)

    content.reindexObject()
    return content

# vim: set ft=python ts=4 sw=4 expandtab :
