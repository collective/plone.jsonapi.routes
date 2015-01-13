# -*- coding: utf-8 -*-

__author__    = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import urllib
import logging

from plone import api as ploneapi
from plone.jsonapi.core import router

from AccessControl import Unauthorized

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import IFolderish
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.CMFPlone.PloneBatch import Batch

# search helpers
from query import search
from query import make_query

# request helpers
from plone.jsonapi.routes import request as req
from plone.jsonapi.routes.exceptions import APIError

from plone.jsonapi.routes.interfaces import IInfo
from plone.jsonapi.routes.interfaces import IDataManager
from plone.jsonapi.routes import underscore as _


logger = logging.getLogger("plone.jsonapi.routes")

PORTAL_IDS = ["0", "portal", "site", "plone"]


#-----------------------------------------------------------------------------
#   Json API (CRUD) Functions
#-----------------------------------------------------------------------------


### GET RECORD
def get_record(uid=None):
    """ returns a single record
    """
    obj = None
    if uid is not None:
        obj = get_object_by_uid(uid)
    else:
        form = req.get_form()
        obj = get_object_by_record(form)
    if obj is None: raise APIError(404, "No object found")
    items = make_items_for([obj])
    return _.first(items)


### GET
def get_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ returns a list of items

    1. If the UID is given, fetch the object directly => should return 1 item
    2. If no UID is given, search for all items of the given portal_type
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid)

    complete = req.get_complete()
    if not complete:
        # if the uid is given, get the complete information set
        complete = uid and True or False

    return make_items_for(results, endpoint, complete=complete)


### GET BATCHED
def get_batched(portal_type=None, request=None, uid=None, endpoint=None):
    """ returns a batched result record (dictionary)
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid)

    # fetch the batch params from the request
    size  = req.get_batch_size()
    start = req.get_batch_start()

    complete = req.get_complete()
    if not complete:
        # if the uid is given, get the complete information set
        complete = uid and True or False

    # return a batched record
    return get_batch(results, size, start, endpoint=endpoint, complete=complete)


### CREATE
def create_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ create items

    1. If the uid is given, get the object and create the content in there
       (assumed that it is folderish)
    2. If the uid is 0, the target folder is assumed the portal.
    3. If there is no uid given, the payload is checked for either a key
        - `parent_uid`  specifies the *uid* of the target folder
        - `parent_path` specifies the *physical path* of the target folder
    """

    # destination where to create the content
    dest = uid and get_object_by_uid(uid) or None

    # extract the data from the request
    records = req.get_request_data()

    results = []
    for record in records:
        if dest is None:
            # find the container for content creation
            dest = find_target_container(record)
        if portal_type is None:
            portal_type = record.get("portal_type", None)
        id = record.get("id", None)
        title = record.get("title", None)
        obj = create_object_in_container(dest, portal_type, id=id, title=title)
        # update the object
        update_object_with_data(obj, record)
        results.append(obj)

    return make_items_for(results, endpoint=endpoint)


### UPDATE
def update_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ update items

    1. If the uid is given, the user wants to update the object with the data
       given in request body
    2. If no uid is given, the user wants to update a bunch of objects.
       -> each record contains either an UID, path or parent_path + id
    """

    # the data to update
    records = req.get_request_data()

    # we have an uid -> try to get an object for it
    obj = get_object_by_uid(uid)
    if obj:
        record = records[0] # ignore other records if we got an uid
        obj = update_object_with_data(obj, record)
        return make_items_for([obj], endpoint=endpoint)

    # no uid -> go through the record items
    results = []
    for record in records:
        obj = get_object_by_record(record)

        # no object found for this record
        if obj is None:
            continue

        # update the object with the given record data
        obj = update_object_with_data(obj, record)
        results.append(obj)

    return make_items_for(results, endpoint=endpoint)


### DELETE
def delete_items(portal_type=None, request=None, uid=None, endpoint=None):
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

    # the data to update
    records = req.get_request_data()

    # we have an uid -> try to get an object for it
    obj = get_object_by_uid(uid)
    if obj:
        info = IInfo(obj)()
        info["deleted"] = delete_object(obj)
        return [info]

    # no uid -> go through the record items
    results = []
    for record in records:
        obj = get_object_by_record(record)

        # no object found for this record
        if obj is None:
            continue

        info = IInfo(obj)()
        info["deleted"] = delete_object(obj)
        results.append(info)

    return results

#-----------------------------------------------------------------------------
#   Data Functions
#-----------------------------------------------------------------------------

def get_search_results(**kw):
    """ search the catalog and return the results

    The request may contain additional query parameters
    """
    query = make_query(**kw)
    return search(query)


def make_items_for(brains_or_objects, endpoint=None, complete=True):
    """ return a list of info dicts

    @param brains_or_objects: List/LazyMap
    """

    # this function extracts the data for one brain or object
    def _block(brain_or_object):

        if req.get("only_children"):
            return get_children(brain_or_object)

        # extract the data using the default info adapter
        info = IInfo(brain_or_object)()

        # might be None for mixed type catalog results, e.g. in the search route
        scoped_endpoint = endpoint
        if scoped_endpoint is None:
            scoped_endpoint = get_endpoint(get_portal_type(brain_or_object))

        info.update(get_url_info(brain_or_object, scoped_endpoint))

        # switch to wake up the object and complete the informations with the
        # data of the content adapter
        if complete:
            obj = get_object(brain_or_object)
            info.update(IInfo(obj)())
            info.update(get_parent_info(obj))
            if req.get_children():
                info.update(get_children(obj))

        return info

    return map(_block, brains_or_objects)


def get_url_info(brain_or_object, endpoint):
    """ returns the url info for the object
    """

    uid = get_uid(brain_or_object)
    return {
        "uid": uid,
        "url": get_url(brain_or_object),
        "api_url": url_for(endpoint, uid=uid),
    }

def get_parent_info(obj):
    """ returns the infos for the parent object
    """

    # special case for the portal route
    if is_root(obj): return {}

    parent   = get_parent(obj)
    endpoint = get_endpoint(parent.portal_type)

    if is_root(parent):
        return {
            "parent_id":  parent.getId(),
            "parent_uid": 0,
            "parent_url": url_for("portal"),
        }

    return {
        "parent_id":  parent.getId(),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, uid=get_uid(parent))
    }


def get_children(obj):
    """ returns the contents for this object
    """

    # ensure we have an object
    obj = get_object(obj)

    if is_folderish(obj) is False:
        return {
            "children": None,
        }

    children = []
    for content in obj.listFolderContents():
        endpoint = get_endpoint(get_portal_type(content))
        child = {
            "uid":     get_uid(content),
            "url":     get_url(content),
            "api_url": url_for(endpoint, uid=get_uid(content)),
        }
        child.update(IInfo(content)())
        children.append(child)

    return {
        "children": children
    }

#-----------------------------------------------------------------------------
#   Batching Helpers
#-----------------------------------------------------------------------------

def get_batch(sequence, size, start=0, endpoint=None, complete=False):
    """ create a batched result record out of a sequence (catalog brains)
    """

    batch = Batch(sequence, size, start)
    return {
        "pagesize": batch.pagesize,
        "next":     make_next_url(batch),
        "previous": make_prev_url(batch),
        "page":     batch.pagenumber,
        "pages":    batch.numpages,
        "count":    batch.sequence_length,
        "items":    make_items_for([b for b in batch], endpoint, complete=complete),
    }


def make_next_url(batch):
    if not batch.has_next:
        return None
    request = req.get_request()
    params = request.form
    params["b_start"] = batch.pagenumber * batch.pagesize
    return "%s?%s" % (request.URL, urllib.urlencode(params))


def make_prev_url(batch):
    if not batch.has_previous:
        return None
    request = req.get_request()
    params = request.form
    params["b_start"] = max(batch.pagenumber - 2, 0) * batch.pagesize
    return "%s?%s" % (request.URL, urllib.urlencode(params))

#-----------------------------------------------------------------------------
#   Functional Helpers
#-----------------------------------------------------------------------------

def get_portal():
    """ get the Plone site
    """
    return ploneapi.portal.getSite()


def get_tool(name):
    """ get a tool by name
    """
    return ploneapi.portal.get_tool(name)


def get_portal_catalog():
    """ get the portal_catalog tool
    """
    return get_tool("portal_catalog")


def get_portal_reference_catalog():
    """ return reference_catalog tool
    """
    return get_tool("reference_catalog")


def get_portal_workflow():
    """ return portal_workflow tool
    """
    return get_tool("portal_workflow")


def is_brain(obj):
    """ checks if the object is a catalog brain
    """
    return ICatalogBrain.providedBy(obj)


def is_root(obj):
    """ checks if the object is the site root
    """
    return ISiteRoot.providedBy(obj)


def is_folderish(obj):
    """ checks if the object is folderish
    """
    return IFolderish.providedBy(obj)


def get_locally_allowed_types(obj):
    """ get the locally allowed types of this object
    """
    if not is_folderish(obj): return []
    method = getattr(obj, "getLocallyAllowedTypes", None)
    if not callable(method): return []
    return method()


def url_for(endpoint, **values):
    """ returns the api url
    """
    try:
        return router.url_for(endpoint, force_external=True, values=values)
    except:
        # XXX plone.jsonapi.core should catch the BuildError of Werkzeug and
        #     throw another error which can be handled here.
        logger.warn("Could not build API URL for endpoint '%s'. No route provider registered?" % endpoint)
        return None


def get_url(obj):
    """ get the absolute url for this object
    """
    if is_brain(obj):
        return obj.getURL()
    return obj.absolute_url()


def get_uid(obj):
    """ get the UID of the brain/object
    """
    if is_brain(obj):
        return obj.UID
    if is_root(obj):
        return 0
    return obj.UID()


def get_portal_type(obj):
    """ return the portal type of this object
    """
    return obj.portal_type


def get_object(brain_or_object):
    """ return the referenced object
    """
    if not is_brain(brain_or_object):
        return brain_or_object
    return brain_or_object.getObject()


def get_parent(brain_or_object):
    """ return the referenced object """
    obj = get_object(brain_or_object)
    return obj.aq_parent


def get_path(brain_or_object):
    """ return the physical path
    """
    if is_brain(brain_or_object):
        return brain_or_object.getPath()
    return "/".join(brain_or_object.getPhysicalPath())


def get_endpoint(portal_type):
    """ get the endpoint for this type """
    # handle portal types with dots
    portal_type = portal_type.split(".").pop()
    # remove whitespaces
    portal_type = portal_type.replace(" ", "")
    # lower and pluralize
    portal_type = portal_type.lower() + "s"

    return portal_type


def get_object_by_record(record):
    """ locate the object by record
    """

    # nothing to do here
    if not record: return None

    if record.get("uid"):
        return get_object_by_uid(record["uid"])
    if record.get("path"):
        return get_object_by_path(record["path"])
    if record.get("parent_path") and record.get("id"):
        path = "/".join([record["parent_path"], record["id"]])
        return get_object_by_path(path)

    logger.warn("get_object_by_record::No object found! record='%r'" % record)
    return None


def get_object_by_uid(uid):
    """ Fetches an object by uid
    """

    # nothing to do here
    if uid is None: return None

    # define uid 0 as the portal object
    if str(uid).lower() in PORTAL_IDS:
        return get_portal()

    # we try to find the object with both catalogs
    pc = get_portal_catalog()
    rc = get_portal_reference_catalog()

    # try to find the object with the reference catalog first
    obj = rc.lookupObject(uid)
    if obj:
        return obj

    # try to find the object with the portal catalog
    res = pc(dict(UID=uid))
    if len(res) > 1:
        raise APIError(500, "More than one object found for UID %s" % uid)
    if not res:
        return None

    return get_object(res[0])


def get_object_by_path(path):
    """ fetch the object by physical path
    """

    # nothing to do here
    if not path: return None

    pc = get_portal_catalog()
    portal = get_portal()
    portal_path = get_path(portal)

    if not path.startswith(portal_path):
        raise APIError(500, "Not a physical path inside the portal")

    if path == portal_path:
        return portal

    res = pc(path=dict(query=path, depth=0))
    if not res:
        return None
    return get_object(res[0])


def mkdir(path):
    """ creates a folder structure by a given path
    """

    container = get_portal()
    segments  = path.split("/")
    curpath   = None

    for n, segment in enumerate(segments):
        # skip the first element
        if not segment:
            continue

        curpath = "/".join(segments[:n+1])
        obj = get_object_by_path(curpath)

        if obj:
            container = obj
            continue

        if not is_folderish(container):
            raise APIError(500, "Object at %s is not a folder" % curpath)

        # create the folder on the go
        container = ploneapi.content.create(
                container, type="Folder", title=segment, save_id=True)

    return container


def find_target_container(record):
    """ find the target container for this record
    """

    parent_uid  = record.get("parent_uid")
    parent_path = record.get("parent_path")

    target = None

    # Try to find the target object
    if parent_uid:
        target = get_object_by_uid(parent_uid)
    elif parent_path:
        target = get_object_by_path(parent_path)
        # Issue 18
        if target is None:
            target = mkdir(parent_path)
    else:
        raise APIError(500, "No target UID/PATH information found")

    if not target:
        raise APIError(500, "No target container found")

    return target


def do_action_for(obj, transition):
    """ perform wf transition """
    return ploneapi.content.transition(obj, transition)


def delete_object(obj):
    """ delete the object """
    # we do not want to delete the site root!
    if is_root(obj): return False
    return ploneapi.content.delete(obj) == None and True or False


def get_current_user():
    """ return the current logged in user """
    return ploneapi.user.get_current()


def create_object_in_container(container, portal_type, id=None, title=None):
    """ creates an object with the given data in the container
    """
    if not is_root(container) and portal_type not in get_locally_allowed_types(container):
        raise APIError(500, "Creation of this portal type is not allowed in this context.")
    return create_object(container=container, id=id, title=title, type=portal_type)


def create_object(**kw):
    defaults = {"save_id": True}
    defaults.update(kw)
    try:
        return ploneapi.content.create(**defaults)
    except Unauthorized:
        raise APIError(401, "You are not allowed to create this content")


def update_object_with_data(content, record):
    """ update the content with the values from records
    """
    dm = IDataManager(content)

    for k, v in record.items():
        if not dm.set(k, v):
            logger.info("update_object_with_data::skipping key=%r", k)
            continue
        logger.info("update_object_with_data::field %r updated with value=%r", k, v)

    # do a wf transition
    if record.get("transition", None):
        t = record.get("transition")
        logger.info(">>> Do Transition '%s' for Object %s", t, content.getId())
        do_action_for(content, t)

    # reindex the object
    content.reindexObject()
    return content

# vim: set ft=python ts=4 sw=4 expandtab :
