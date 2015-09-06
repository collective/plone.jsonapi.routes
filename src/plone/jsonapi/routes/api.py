# -*- coding: utf-8 -*-

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
from plone.jsonapi.routes.interfaces import IBatch
from plone.jsonapi.routes.interfaces import IDataManager
from plone.jsonapi.routes import underscore as _

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

logger = logging.getLogger("plone.jsonapi.routes")

PORTAL_IDS = ["0", "portal", "site", "plone", "root"]


# -----------------------------------------------------------------------------
#   Json API (CRUD) Functions
# -----------------------------------------------------------------------------


# GET RECORD
def get_record(uid=None):
    """ returns a single record
    """
    obj = None
    if uid is not None:
        obj = get_object_by_uid(uid)
    else:
        form = req.get_form()
        obj = get_object_by_record(form)
    if obj is None:
        raise APIError(404, "No object found")
    items = make_items_for([obj])
    return _.first(items)


# GET
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


# GET BATCHED
def get_batched(portal_type=None, request=None, uid=None, endpoint=None):
    """ returns a batched result record (dictionary)
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid)

    # fetch the batch params from the request
    size = req.get_batch_size()
    start = req.get_batch_start()

    complete = req.get_complete()
    if not complete:
        # if the uid is given, get the complete information set
        complete = uid and True or False

    # return a batched record
    return get_batch(results, size, start, endpoint=endpoint,
                     complete=complete)


# CREATE
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

    if not results:
        raise APIError(400, "No Objects could be created")

    return make_items_for(results, endpoint=endpoint)


# UPDATE
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
        record = records[0]  # ignore other records if we got an uid
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

    if not results:
        raise APIError(400, "No Objects could be updated")

    return make_items_for(results, endpoint=endpoint)


# DELETE
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

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # We don't want to delete the portal object
    if filter(lambda o: is_root(o), objects):
        raise APIError(400, "Can not delete the portal object")

    results = []
    for obj in objects:
        info = IInfo(obj)()
        info["deleted"] = delete_object(obj)
        results.append(info)

    if not results:
        raise APIError(404, "No Objects could be found")

    return results


# CUT
def cut_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ cut items
    """

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # No objects could be found, bail out
    if not objects:
        raise APIError(404, "No Objects could be found")

    # We support only to cut a single object
    if len(objects) > 1:
        raise APIError(400, "Can only cut one object at a time")

    # We don't want to cut the portal object
    if filter(lambda o: is_root(o), objects):
        raise APIError(400, "Can not cut the portal object")

    # cut the object
    obj = objects[0]
    obj.aq_parent.manage_cutObjects(obj.getId(), REQUEST=request)
    request.response.setHeader("Content-Type", "application/json")
    info = IInfo(obj)()

    return [info]


# COPY
def copy_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ copy items
    """

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # No objects could be found, bail out
    if not objects:
        raise APIError(404, "No Objects could be found")

    # We support only to copy a single object
    if len(objects) > 1:
        raise APIError(400, "Can only copy one object at a time")

    # We don't want to copy the portal object
    if filter(lambda o: is_root(o), objects):
        raise APIError(400, "Can not copy the portal object")

    # cut the object
    obj = objects[0]
    obj.aq_parent.manage_copyObjects(obj.getId(), REQUEST=request)
    request.response.setHeader("Content-Type", "application/json")
    info = IInfo(obj)()

    return [info]


# PASTE
def paste_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ paste items
    """

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # No objects could be found, bail out
    if not objects:
        raise APIError(404, "No Objects could be found")

    # check if the cookie is there
    cookie = req.get_cookie("__cp")
    if cookie is None:
        raise APIError(400, "No data found to paste")

    # We support only to copy a single object
    if len(objects) > 1:
        raise APIError(400, "Can only paste to one location")

    # cut the object
    obj = objects[0]

    # paste the object
    results = obj.manage_pasteObjects(cookie)

    out = []
    for result in results:
        new_id = result.get("new_id")
        pasted = obj.get(new_id)
        if pasted:
            out.append(IInfo(pasted)())

    return out


# -----------------------------------------------------------------------------
#   Data Functions
# -----------------------------------------------------------------------------

def get_search_results(**kw):
    """ search the catalog and return the results

    The request may contain additional query parameters
    """
    if kw.get("portal_type") == "Plone Site":
        return [get_portal()]
    query = make_query(**kw)
    return search(query)


def make_items_for(brains_or_objects, endpoint=None, complete=True):
    """ return a list of info dicts

    @param brains_or_objects: List/LazyMap
    """

    # this function extracts the data for one brain or object
    def _block(brain_or_object):

        # extract the data using the default info adapter
        info = IInfo(brain_or_object)()

        # wake up the object and extract the complete data
        if complete:
            obj = get_object(brain_or_object)
            info.update(IInfo(obj)())
            # also include the parent url info
            parent = get_parent_info(obj)
            info.update(parent)

        # update with url info
        url_info = get_url_info(brain_or_object, endpoint)
        info.update(url_info)

        # include an array of child contents
        if req.get_children():
            children = get_children(brain_or_object, complete)
            info.update(children)

        return info

    return map(_block, brains_or_objects)


def get_url_info(brain_or_object, endpoint=None):
    """ returns the url info for the object
    """

    # If no endpoint was given, guess the endpoint by portal type
    if endpoint is None:
        endpoint = get_endpoint(brain_or_object)

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
    if is_root(obj):
        return {}

    parent = get_parent(obj)
    endpoint = get_endpoint(parent)

    if is_root(parent):
        return {
            "parent_id":  parent.getId(),
            "parent_uid": 0,
            "parent_url": url_for("plonesites", uid=0),
        }

    return {
        "parent_id":  parent.getId(),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, uid=get_uid(parent))
    }


def get_children(brain_or_object, complete=False):
    """ returns the contents for this object
    """

    children = []

    for brain in get_contents(brain_or_object):
        child = IInfo(brain)()
        child.update(get_url_info(brain))

        # if the complete flag is set, we include the full object info for the
        # child contents.
        if complete:
            # wake up the object
            obj = get_object(brain)
            # extract and include schema field values
            child.update(IInfo(obj)())
        children.append(child)

    return {
        "child_count": len(children),
        "children": children
    }


# -----------------------------------------------------------------------------
#   Batching Helpers
# -----------------------------------------------------------------------------

def get_batch(sequence, size, start=0, endpoint=None, complete=False):
    """ create a batched result record out of a sequence (catalog brains)
    """

    # we call an adapter here to allow backwards compatibility hooks
    batch = IBatch(Batch(sequence, size, start))

    return {
        "pagesize": batch.get_pagesize(),
        "next":     batch.make_next_url(),
        "previous": batch.make_prev_url(),
        "page":     batch.get_pagenumber(),
        "pages":    batch.get_numpages(),
        "count":    batch.get_sequence_length(),
        "items":    make_items_for([b for b in batch.get_batch()],
                                   endpoint, complete=complete),
    }


# -----------------------------------------------------------------------------
#   Functional Helpers
# -----------------------------------------------------------------------------

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


def is_brain(brain_or_object):
    """ checks if the object is a catalog brain
    """
    return ICatalogBrain.providedBy(brain_or_object)


def is_root(brain_or_object):
    """ checks if the object is the site root
    """
    return ISiteRoot.providedBy(brain_or_object)


def is_folderish(brain_or_object):
    """ checks if the object is folderish
    """
    if is_brain(brain_or_object):
        return brain_or_object.is_folderish
    return IFolderish.providedBy(brain_or_object)


def get_locally_allowed_types(obj):
    """ get the locally allowed types of this object
    """
    if not is_folderish(obj):
        return []
    method = getattr(obj, "getLocallyAllowedTypes", None)
    if not callable(method):
        return []
    return method()


def url_for(endpoint, **values):
    """ returns the api url
    """
    try:
        return router.url_for(endpoint, force_external=True, values=values)
    except:
        # XXX plone.jsonapi.core should catch the BuildError of Werkzeug and
        #     throw another error which can be handled here.
        logger.warn("Could not build API URL for endpoint '%s'. "
                    "No route provider registered?" % endpoint)
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


def get_portal_type(brain_or_object):
    """ return the portal type of this object
    """
    return brain_or_object.portal_type


def get_object(brain_or_object):
    """ return the referenced object
    """
    if is_brain(brain_or_object):
        return brain_or_object.getObject()
    return brain_or_object


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


def get_contents(brain_or_object, depth=1):
    """ return the folder contents
    """
    pc = get_portal_catalog()
    contents = pc(path={
        "query": get_path(brain_or_object),
        "depth": depth})
    return contents


def get_endpoint(brain_or_object):
    """ get the endpoint for this object

        The endpoint is used to generate the api url for this content.
    """

    portal_type = get_portal_type(brain_or_object)
    # handle portal types with dots
    portal_type = portal_type.split(".").pop()
    # remove whitespaces
    portal_type = portal_type.replace(" ", "")
    # lower and pluralize
    portal_type = portal_type.lower() + "s"

    return portal_type


def find_objects(uid=None):
    """ locate objects

    1. get the object from the given uid
    2. fetch objects specified in the request parameters
    3. fetch objects located in the request body
    """
    # The objects to cut
    objects = []

    # get the object by the given uid or try to find it by the request
    # parameters
    obj = get_object_by_uid(uid) or get_object_by_request()

    if obj:
        objects.append(obj)
    else:
        # no uid -> go through the record items
        records = req.get_request_data()
        for record in records:
            # try to get the object by the given record
            obj = get_object_by_record(record)

            # no object found for this record
            if obj is None:
                continue
            objects.append(obj)

    return objects


def get_object_by_request():
    """ locate the object by the request parameters
    """
    form = req.get_form()
    return get_object_by_record(form)


def get_object_by_record(record):
    """ locate the object by the given record (dictionary).
    The record is usually contained in the request.body or in the request.form
    """

    # nothing to do here
    if not record:
        return None

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
    if uid is None:
        return None

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
        raise APIError(400, "More than one object found for UID %s" % uid)
    if not res:
        return None

    return get_object(res[0])


def get_object_by_path(path):
    """ fetch the object by physical path
    """

    # nothing to do here
    if not path:
        return None

    pc = get_portal_catalog()
    portal = get_portal()
    portal_path = get_path(portal)

    if not path.startswith(portal_path):
        raise APIError(404, "Not a physical path inside the portal")

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
    segments = path.split("/")
    curpath = None

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
            raise APIError(400, "Object at %s is not a folder" % curpath)

        # create the folder on the go
        container = ploneapi.content.create(
            container, type="Folder", id=segment)

    return container


def find_target_container(record):
    """ find the target container for this record
    """

    parent_uid = record.get("parent_uid")
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
        raise APIError(404, "No target UID/PATH information found")

    if not target:
        raise APIError(404, "No target container found")

    return target


def do_action_for(brain_or_object, transition):
    """ perform wf transition """
    obj = get_object(brain_or_object)
    return ploneapi.content.transition(obj, transition)


def delete_object(brain_or_object):
    """ delete the object """

    obj = get_object(brain_or_object)
    # we do not want to delete the site root!
    if is_root(obj):
        raise APIError(401, "Removing the Portal is not allowed")
    try:
        return ploneapi.content.delete(obj) is None and True or False
    except Unauthorized:
        raise APIError(401, "Not allowed to delete object '%s'" % obj.getId())


def get_current_user():
    """ return the current logged in user """
    return ploneapi.user.get_current()


def create_object_in_container(container, portal_type, id=None, title=None):
    """ creates an object with the given data in the container
    """
    allowed_types = get_locally_allowed_types(container)
    if not is_root(container) and portal_type not in allowed_types:
        raise APIError(500, "Creation of this portal type"
                            "is not allowed in this context.")

    return create_object(container=container, id=id, title=title,
                         type=portal_type)


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
    if dm is None:
        raise APIError(400, "Update on this object is not allowed")

    # Iterate through record items
    for k, v in record.items():
        try:
            success = dm.set(k, v, **record)
        except Unauthorized:
            raise APIError(401, "Not allowed to set the field '%s'" % k)

        if not success:
            logger.warn("update_object_with_data::skipping key=%r", k)
            continue

        logger.debug("update_object_with_data::field %r updated", k)

    # do a wf transition
    if record.get("transition", None):
        t = record.get("transition")
        logger.info(">>> Do Transition '%s' for Object %s", t, content.getId())
        do_action_for(content, t)

    # reindex the object
    content.reindexObject()
    return content
