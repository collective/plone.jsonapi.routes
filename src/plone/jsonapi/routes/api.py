# -*- coding: utf-8 -*-

import logging
import pkg_resources

from plone import api as ploneapi
from plone.jsonapi.core import router

from AccessControl import Unauthorized

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import IFolderish
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.interfaces import IConstrainTypes

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

_marker = object()

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
    complete = req.get_complete(default=_marker)
    if complete is _marker:
        complete = True
    items = make_items_for([obj], complete=complete)
    return _.first(items)


# GET
def get_items(portal_type=None, request=None, uid=None, endpoint=None):
    """ returns a list of items

    1. If the UID is given, fetch the object directly => should return 1 item
    2. If no UID is given, search for all items of the given portal_type
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid)

    # check for existing complete flag
    complete = req.get_complete(default=_marker)
    if complete is _marker:
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

    # check for existing complete flag
    complete = req.get_complete(default=_marker)
    if complete is _marker:
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
    """Search the catalog and return the results

    :returns: Catalog search results
    :rtype: list/Products.ZCatalog.Lazy.LazyMap
    """

    # allow to search for the Plone site
    if kw.get("portal_type") == "Plone Site":
        portal = get_portal()
        if portal:
            return [portal]
        else:
            return []
    elif kw.get("id") in PORTAL_IDS:
        return [get_portal()]
    elif kw.get("uid") in PORTAL_IDS:
        return [get_portal()]

    # build and execute a catalog query
    query = make_query(**kw)
    return search(query)


def make_items_for(brains_or_objects, endpoint=None, complete=False):
    """Generate API compatible data items for the given list of brains/objects

    :param brains_or_objects: List of objects or brains
    :type brains_or_objects: list/Products.ZCatalog.Lazy.LazyMap
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: A list of extracted data items
    :rtype: list
    """

    # check if the user wants to include children
    include_children = req.get_children(False)

    def extract_data(brain_or_object):
        info = get_info(brain_or_object, endpoint=endpoint, complete=complete)
        if include_children and is_folderish(brain_or_object):
            info.update(get_children_info(brain_or_object, complete=complete))
        return info

    return map(extract_data, brains_or_objects)


def get_info(brain_or_object, endpoint=None, complete=False):
    """Extract the data from the catalog brain or object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: Data mapping for the object/catalog brain
    :rtype: dict
    """

    # extract the data from the initial object with the proper adapter
    info = IInfo(brain_or_object).to_dict()

    # update with url info (always included)
    url_info = get_url_info(brain_or_object, endpoint)
    info.update(url_info)

    # include the parent url info
    parent = get_parent_info(brain_or_object)
    info.update(parent)

    # add the complete data of the object if requested
    # -> requires to wake up the object if it is a catalog brain
    if complete:
        # ensure we have a full content object
        obj = get_object(brain_or_object)
        # get the compatible adapter
        adapter = IInfo(obj)
        # update the data set with the complete information
        info.update(adapter.to_dict())

        # add workflow data if the user requested it
        # -> only possible if `?complete=yes`
        if req.get_workflow(False):
            workflow = get_workflow_info(obj)
            info.update({"workflow": workflow})

        # add sharing data if the user requested it
        # -> only possible if `?complete=yes`
        if req.get_sharing(False):
            sharing = get_sharing_info(obj)
            info.update({"sharing": sharing})

    return info


def get_url_info(brain_or_object, endpoint=None):
    """Generate url information for the content object/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: URL information mapping
    :rtype: dict
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


def get_workflow_info(brain_or_object, endpoint=None):
    """Generate workflow information of the (first) assigned workflow

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: Workflow information mapping
    :rtype: dict
    """

    # ensure we have a full content object
    obj = get_object(brain_or_object)

    # get the portal workflow tool
    wf_tool = get_tool("portal_workflow")

    # the assigned workflows of this object
    wfs = wf_tool.getWorkflowsFor(obj)

    # no worfkflows assigned -> return
    if not wfs:
        return {}

    # get the first one
    workflow = wfs[0]

    # get the status info of the current state (dictionary)
    status = wf_tool.getStatusOf(workflow.getId(), obj)

    # https://github.com/collective/plone.jsonapi.routes/issues/33
    if not status:
        return {}

    # get the current review_status
    current_state_id = status.get("review_state", None)

    # get the wf status object
    current_status = workflow.states[current_state_id]

    # get the title of the current status
    current_state_title = current_status.title

    def to_transition_info(transition):
        """ return the transition information
        """
        return {
            "value":   transition["id"],
            "display": transition["description"],
            "url":     transition["url"],
        }

    # get the transition informations
    transitions = map(to_transition_info, wf_tool.getTransitionsFor(obj))

    return {
        "workflow":     workflow.getId(),
        "status":       current_state_title,
        "review_state": current_state_id,
        "transitions":  transitions
    }


def get_parent_info(brain_or_object, endpoint=None):
    """Generate url information for the parent object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param endpoint: The named URL endpoint for the root of the items
    :type endpoint: str/unicode
    :returns: URL information mapping
    :rtype: dict
    """

    # special case for the portal object
    if is_root(brain_or_object):
        return {}

    # get the parent object
    parent = get_parent(brain_or_object)

    # fall back if no endpoint specified
    if endpoint is None:
        endpoint = get_endpoint(parent)

    # return portal information
    if is_root(parent):
        return {
            "parent_id": get_id(parent),
            "parent_uid": 0,
            "parent_url": url_for("plonesites", uid=0),
        }

    return {
        "parent_id": get_id(parent),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, uid=get_uid(parent))
    }


def get_children_info(brain_or_object, complete=False):
    """Generate data items of the contained contents

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param complete: Flag to wake up the object and fetch all data
    :type complete: bool
    :returns: info mapping of contained content items
    :rtype: list
    """

    # fetch the contents (if folderish)
    children = get_contents(brain_or_object)

    def extract_data(brain_or_object):
        return get_info(brain_or_object, complete=complete)
    items = map(extract_data, children)

    return {
        "children_count": len(items),
        "children": items
    }


def get_sharing_info(brain_or_object):
    """Generate sharing info of the given object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: sharing information of the object
    :rtype: dict
    """

    obj = get_object(brain_or_object)
    sharing = get_sharing_view_for(obj)

    return {
        "role_settings": sharing.role_settings(),
        "inherit": sharing.inherited()
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

def get_plone_version():
    """Get the Plone version

    :returns: Plone version
    :rtype: str or list
    """
    dist = pkg_resources.get_distribution("Plone")
    return dist.version


def is_plone4():
    """Check for Plone

    :returns: True if Plone 4
    :rtype: boolean
    """
    version = get_plone_version()
    return version.startswith("4")


def is_plone5():
    """Check for Plone 5 series

    :returns: True if Plone 5
    :rtype: boolean
    """
    version = get_plone_version()
    return version.startswith("5")


def get_portal():
    """Get the portal object

    :returns: Portal object
    :rtype: object
    """
    return ploneapi.portal.getSite()


def get_tool(name):
    """Get a portal tool by name

    :param name: The name of the tool, e.g. `portal_catalog`
    :type name: string
    :returns: Portal Tool
    :rtype: object
    """
    return ploneapi.portal.get_tool(name)


def get_portal_catalog():
    """Get the portal catalog tool

    :returns: Portal Catalog Tool
    :rtype: object
    """
    return get_tool("portal_catalog")


def get_portal_reference_catalog():
    """Get the portal reference catalog tool

    :returns: Portal Reference Catalog Tool
    :rtype: object
    """
    return get_tool("reference_catalog")


def get_portal_workflow():
    """Get the portal workflow tool

    :returns: Portal Workflow Tool
    :rtype: object
    """
    return get_tool("portal_workflow")


def get_sharing_view_for(obj):
    """Get the sharing view

    :returns: Sharing view for the given object
    :rtype: object
    """
    return ploneapi.content.get_view('sharing', obj, req.get_request())


def is_brain(brain_or_object):
    """Checks if the passed in object is a portal catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is a catalog brain
    :rtype: bool
    """
    return ICatalogBrain.providedBy(brain_or_object)


def is_root(brain_or_object):
    """Checks if the passed in object is the portal root object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is the portal root object
    :rtype: bool
    """
    return ISiteRoot.providedBy(brain_or_object)


def is_folderish(brain_or_object):
    """Checks if the passed in object is folderish

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is folderish
    :rtype: bool
    """
    if is_brain(brain_or_object):
        return brain_or_object.is_folderish
    return IFolderish.providedBy(brain_or_object)


def get_locally_allowed_types(brain_or_object):
    """Checks if the passed in object is folderish

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: A list of locally allowed content types
    :rtype: list
    """
    if not is_folderish(brain_or_object):
        return []
    # ensure we have an object
    obj = get_object(brain_or_object)
    method = getattr(obj, "getLocallyAllowedTypes", None)
    if method is None:
        constrains = IConstrainTypes(obj, None)
        if constrains:
            method = constrains.getLocallyAllowedTypes
    if not callable(method):
        return []
    return method()


def url_for(endpoint, **values):
    """Looks up the API URL for the given endpoint

    :param endpoint: The name of the registered route (aka endpoint)
    :type endpoint: string
    :returns: External URL for this endpoint
    :rtype: string/None
    """
    try:
        return router.url_for(endpoint, force_external=True, values=values)
    except Exception:
        # XXX plone.jsonapi.core should catch the BuildError of Werkzeug and
        #     throw another error which can be handled here.
        logger.debug("Could not build API URL for endpoint '%s'. "
                     "No route provider registered?" % endpoint)
        return None


def get_url(brain_or_object):
    """Get the absolute Plone URL for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone URL
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.getURL()
    return brain_or_object.absolute_url()


def get_id(brain_or_object):
    """Get the Plone ID for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone ID
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.getId
    return brain_or_object.getId()


def get_uid(brain_or_object):
    """Get the Plone UID for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Plone UID
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.UID
    if is_root(brain_or_object):
        return 0
    return brain_or_object.UID()


def get_portal_type(brain_or_object):
    """Get the portal type for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Portal type
    :rtype: string
    """
    return brain_or_object.portal_type


def get_object(brain_or_object):
    """Get the full content object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Content object
    :rtype: object
    """
    if is_brain(brain_or_object):
        return brain_or_object.getObject()
    return brain_or_object


def get_parent(brain_or_object):
    """Locate the parent object of the content/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: parent object
    :rtype: ATContentType/DexterityContentType/PloneSite/CatalogBrain
    """

    if is_brain(brain_or_object):
        parent_path = get_parent_path(brain_or_object)

        # parent is the portal object
        if parent_path == get_path(get_portal()):
            return get_portal()

        # query for the parent path
        pc = get_portal_catalog()
        results = pc(path={
            "query": parent_path,
            "depth": 0})

        # fallback to the object
        if not results:
            return get_object(brain_or_object).aq_parent
        # return the brain
        return results[0]

    return brain_or_object.aq_parent


def get_parent_path(brain_or_object):
    """Calculate the physical parent path of this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Physical path of the parent object
    :rtype: string
    """
    if is_brain(brain_or_object):
        path = get_path(brain_or_object)
        return path.rpartition("/")[0]
    return get_path(brain_or_object.aq_parent)


def get_path(brain_or_object):
    """Calculate the physical path of this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Physical path of the object
    :rtype: string
    """
    if is_brain(brain_or_object):
        return brain_or_object.getPath()
    return "/".join(brain_or_object.getPhysicalPath())


def get_contents(brain_or_object, depth=1):
    """Lookup folder contents for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of contained contents
    :rtype: list/Products.ZCatalog.Lazy.LazyMap
    """
    pc = get_portal_catalog()
    contents = pc(path={
        "query": get_path(brain_or_object),
        "depth": depth})
    return contents


def get_endpoint(brain_or_object):
    """Calculate the endpoint for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Endpoint for this object (pluralized portal type)
    :rtype: string
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
    """Find the object by its UID

    1. get the object from the given uid
    2. fetch objects specified in the request parameters
    3. fetch objects located in the request body

    :param uid: The UID of the object to find
    :type uid: string
    :returns: List of found objects
    :rtype: list
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
    """Find an object by request parameters

    Inspects request parameters to locate an object

    :returns: Found Object or None
    :rtype: object
    """
    form = req.get_form()
    return get_object_by_record(form)


def get_object_by_record(record):
    """Find an object by a given record

    Inspects request the record to locate an object

    :param record: A dictionary representation of an object
    :type record: dict
    :returns: Found Object or None
    :rtype: object
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
    """Find an object by a given UID

    :param uid: The UID of the object to find
    :type uid: string
    :returns: Found Object or None
    :rtype: object
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
    """Find an object by a given physical path

    :param path: The physical path of the object to find
    :type path: string
    :returns: Found Object or None
    :rtype: object
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
    """Crate a folder structure by a given path

    Behavior is similar to `mkdir -p`

    :param path: The physical path of the folder
    :type path: string
    :returns: folder located at the path
    :rtype: object
    """
    container = get_portal()
    segments = path.split("/")
    curpath = None

    for n, segment in enumerate(segments):
        # skip the first element
        if not segment:
            continue

        curpath = "/".join(segments[:n + 1])
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
    """Locates a target container for the given record

    :param record: The dictionary representation of a content object
    :type record: dict
    :returns: folder which contains the object
    :rtype: object
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
    """Perform a workflow transition

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param transition: The workflow transition to perform, e.g. `publish`
    :type transition: string
    :returns: Nothing
    :rtype: None
    """
    obj = get_object(brain_or_object)
    return ploneapi.content.transition(obj, transition)


def update_sharing_for(brain_or_object, sharing):
    """Perform a sharing update

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param sharing: The sharing dictionary as returned from the API
    :type sharing: dict
    :returns: change status
    :rtype: boolean
    """

    obj = get_object(brain_or_object)
    view = get_sharing_view_for(obj)

    # 1. Update inherit settings for this object
    inherit = sharing.get("inherit", _marker)
    if inherit is not _marker:
        view.update_inherit(inherit)

    def fix_role_settings(settings):
        # transform the roles to be compatible with the sharing views API
        roles = settings.get("roles", {})
        settings["roles"] = [k for (k, v) in roles.items() if v]
        return settings

    # 2. Prepare data for the sharing view API
    role_settings = sharing.get("role_settings", [])
    settings = map(fix_role_settings, role_settings)

    # disable CSRF
    req.disable_csrf_protection()

    # 3. Update sharing settings
    return view.update_role_settings(settings)


def delete_object(brain_or_object):
    """Delete the given object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Nothing
    :rtype: None
    """
    obj = get_object(brain_or_object)
    # we do not want to delete the site root!
    if is_root(obj):
        raise APIError(401, "Removing the Portal is not allowed")
    try:
        return ploneapi.content.delete(obj) is None and True or False
    except Unauthorized:
        raise APIError(401, "Not allowed to delete object '%s'" % obj.getId())


def get_current_user():
    """Get the current logged in user

    :returns: Member
    :rtype: object
    """
    return ploneapi.user.get_current()


def create_object_in_container(container, portal_type, id=None, title=None):
    """Creates a content object in the specified container

    :param container: A single folderish catalog brain or content object
    :type container: ATContentType/DexterityContentType/CatalogBrain
    :param portal_type: The portal type to create
    :type portal_type: string
    :returns: The new content object
    :rtype: object
    """
    container = get_object(container)
    allowed_types = get_locally_allowed_types(container)
    if not is_root(container) and portal_type not in allowed_types:
        raise APIError(500, "Creation of this portal type"
                            "is not allowed in this context.")

    return create_object(container=container, id=id, title=title,
                         type=portal_type)


def create_object(**kw):
    """Creates an object

    :returns: The new created content object
    :rtype: object
    """
    defaults = {"save_id": True}
    defaults.update(kw)
    try:
        return ploneapi.content.create(**defaults)
    except Unauthorized:
        raise APIError(401, "You are not allowed to create this content")


def update_object_with_data(content, record):
    """Update the content with the record data

    :param content: A single folderish catalog brain or content object
    :type content: ATContentType/DexterityContentType/CatalogBrain
    :param record: The data to update
    :type record: dict
    :returns: The updated content object
    :rtype: object
    """

    # ensure we have a full content object
    content = get_object(content)

    # get the proper data manager
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
        logger.debug(">>> Do Transition '%s' for Object %s", t, content.getId())
        do_action_for(content, t)

    # do a sharing update
    if record.get("sharing", None):
        s = record.get("sharing")
        logger.debug(">>> Update sharing to %r for Object %s", s, content.getId())
        update_sharing_for(content, s)

    # reindex the object
    content.reindexObject()
    return content
