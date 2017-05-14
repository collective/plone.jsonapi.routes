# -*- coding: utf-8 -*-

import json
import datetime
import pkg_resources

from zope import interface
from zope.schema import getFields
from zope.component import getMultiAdapter

from plone import api as ploneapi
from plone.jsonapi.core import router
from plone.dexterity.interfaces import IDexterityContent
from plone.behavior.interfaces import IBehaviorAssignable

from DateTime import DateTime
from AccessControl import Unauthorized
from Acquisition import ImplicitAcquisitionWrapper

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.interfaces import IFolderish
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.CMFPlone.PloneBatch import Batch
from plone.api.exc import InvalidParameterError

try:
    pkg_resources.get_distribution('Products.Archetypes')
except pkg_resources.DistributionNotFound:
    class IBaseObject(interface.Interface):
        """Fake Products.Archetypes.interfaces.base.IBaseObject"""
else:
    from Products.Archetypes.interfaces.base import IBaseObject


# request helpers
from plone.jsonapi.routes import request as req
from plone.jsonapi.routes.exceptions import APIError

from plone.jsonapi.routes import logger
from plone.jsonapi.routes.interfaces import IInfo
from plone.jsonapi.routes.interfaces import IBatch
from plone.jsonapi.routes.interfaces import ICatalog
from plone.jsonapi.routes.interfaces import ICatalogQuery
from plone.jsonapi.routes.interfaces import IDataManager
from plone.jsonapi.routes.interfaces import IFieldManager
from plone.jsonapi.routes import underscore as u

__author__ = 'Ramon Bartl <rb@ridingbytes.com>'
__docformat__ = 'plaintext'

_marker = object()

PORTAL_IDS = ["0", "portal", "site", "plone", "root", "plone site"]


# -----------------------------------------------------------------------------
#   JSON API (CRUD) Functions
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
        fail(404, "No object found")
    complete = req.get_complete(default=_marker)
    if complete is _marker:
        complete = True
    items = make_items_for([obj], complete=complete)
    return u.first(items)


# GET
def get_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ returns a list of items

    1. If the UID is given, fetch the object directly => should return 1 item
    2. If no UID is given, search for all items of the given portal_type
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid, **kw)

    # check for existing complete flag
    complete = req.get_complete(default=_marker)
    if complete is _marker:
        # if the uid is given, get the complete information set
        complete = uid and True or False

    return make_items_for(results, endpoint, complete=complete)


# GET BATCHED
def get_batched(portal_type=None, uid=None, endpoint=None, **kw):
    """ returns a batched result record (dictionary)
    """

    # fetch the catalog results
    results = get_search_results(portal_type=portal_type, uid=uid, **kw)

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
def create_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ create items

    1. If the uid is given, get the object and create the content in there
       (assumed that it is folderish)
    2. If the uid is 0, the target folder is assumed the portal.
    3. If there is no uid given, the payload is checked for either a key
        - `parent_uid`  specifies the *uid* of the target folder
        - `parent_path` specifies the *physical path* of the target folder
    """

    # disable CSRF
    req.disable_csrf_protection()

    # destination where to create the content
    container = uid and get_object_by_uid(uid) or None

    # extract the data from the request
    records = req.get_request_data()

    results = []
    for record in records:
        if container is None:
            # find the container for content creation
            container = find_target_container(record)

        if portal_type is None:
            # try to fetch the portal type out of the request data
            portal_type = record.pop("portal_type", None)

        # Check if we have a container and a portal_type
        if not all([container, portal_type]):
            fail(400, "Please provide a container path/uid and portal_type")

        # create the object and pass in the record data
        obj = create_object(container, portal_type, **record)
        results.append(obj)

    if not results:
        fail(400, "No Objects could be created")

    return make_items_for(results, endpoint=endpoint)


# UPDATE
def update_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ update items

    1. If the uid is given, the user wants to update the object with the data
       given in request body
    2. If no uid is given, the user wants to update a bunch of objects.
       -> each record contains either an UID, path or parent_path + id
    """

    # disable CSRF
    req.disable_csrf_protection()

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
        fail(400, "No Objects could be updated")

    return make_items_for(results, endpoint=endpoint)


# DELETE
def delete_items(portal_type=None, uid=None, endpoint=None, **kw):
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

    # disable CSRF
    req.disable_csrf_protection()

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # We don't want to delete the portal object
    if filter(lambda o: is_root(o), objects):
        fail(400, "Can not delete the portal object")

    results = []
    for obj in objects:
        info = IInfo(obj)()
        info["deleted"] = delete_object(obj)
        results.append(info)

    if not results:
        fail(404, "No Objects could be found")

    return results


# CUT
def cut_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ cut items
    """

    # disable CSRF
    req.disable_csrf_protection()

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # No objects could be found, bail out
    if not objects:
        fail(404, "No Objects could be found")

    # We support only to cut a single object
    if len(objects) > 1:
        fail(400, "Can only cut one object at a time")

    # We don't want to cut the portal object
    if filter(lambda o: is_root(o), objects):
        fail(400, "Can not cut the portal object")

    # cut the object
    obj = objects[0]
    request = req.getRequest()
    obj.aq_parent.manage_cutObjects(obj.getId(), REQUEST=request)
    request.response.setHeader("Content-Type", "application/json")
    info = IInfo(obj)()

    return [info]


# COPY
def copy_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ copy items
    """

    # disable CSRF
    req.disable_csrf_protection()

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # No objects could be found, bail out
    if not objects:
        fail(404, "No Objects could be found")

    # We support only to copy a single object
    if len(objects) > 1:
        fail(400, "Can only copy one object at a time")

    # We don't want to copy the portal object
    if filter(lambda o: is_root(o), objects):
        fail(400, "Can not copy the portal object")

    # cut the object
    obj = objects[0]
    request = req.getRequest()
    obj.aq_parent.manage_copyObjects(obj.getId(), REQUEST=request)
    request.response.setHeader("Content-Type", "application/json")
    info = IInfo(obj)()

    return [info]


# PASTE
def paste_items(portal_type=None, uid=None, endpoint=None, **kw):
    """ paste items
    """

    # disable CSRF
    req.disable_csrf_protection()

    # try to find the requested objects
    objects = find_objects(uid=uid)

    # No objects could be found, bail out
    if not objects:
        fail(404, "No Objects could be found")

    # check if the cookie is there
    cookie = req.get_cookie("__cp")
    if cookie is None:
        fail(400, "No data found to paste")

    # We support only to copy a single object
    if len(objects) > 1:
        fail(400, "Can only paste to one location")

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

def search(**kw):
    """Search the catalog
    """
    portal = get_portal()
    catalog = ICatalog(portal)
    catalog_query = ICatalogQuery(catalog)
    query = catalog_query.make_query(**kw)
    return catalog(query)


def get_search_results(portal_type=None, uid=None, **kw):
    """Search the catalog and return the results

    :returns: Catalog search results
    :rtype: list or Products.ZCatalog.Lazy.LazyMap
    """

    # If we have an UID, return the object immediately
    if uid is not None:
        logger.info("UID '%s' found, returning the object immediately" % uid)
        return u.to_list(get_object_by_uid(uid))

    # allow to search search for the Plone Site with portal_type
    include_portal = False
    if u.to_string(portal_type) == "Plone Site":
        include_portal = True

    # The request may contain a list of portal_types, e.g.
    # `?portal_type=Document&portal_type=Plone Site`
    if "Plone Site" in u.to_list(req.get("portal_type")):
        include_portal = True

    # Build and execute a catalog query
    results = search(portal_type=portal_type, uid=uid, **kw)

    if include_portal:
        results = list(results) + u.to_list(get_portal())

    return results


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
    portal_type = get_portal_type(brain_or_object)
    resource = portal_type_to_resource(portal_type)

    return {
        "uid": uid,
        "url": get_url(brain_or_object),
        "api_url": url_for(endpoint, resource=resource, uid=uid),
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
            "value": transition["id"],
            "display": transition["description"],
            "url": transition["url"],
        }

    # get the transition informations
    transitions = map(to_transition_info, wf_tool.getTransitionsFor(obj))

    return {
        "workflow": workflow.getId(),
        "status": current_state_title,
        "review_state": current_state_id,
        "transitions": transitions
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
    portal_type = get_portal_type(parent)
    resource = portal_type_to_resource(portal_type)

    # fall back if no endpoint specified
    if endpoint is None:
        endpoint = get_endpoint(parent)

    return {
        "parent_id": get_id(parent),
        "parent_uid": get_uid(parent),
        "parent_url": url_for(endpoint, resource=resource, uid=get_uid(parent))
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


def get_file_info(obj, fieldname, default=None):
    """Extract file data from a file field

    :param obj: Content object
    :type obj: ATContentType/DexterityContentType
    :param fieldname: Schema name of the field
    :type fieldname: str/unicode
    :returns: File data mapping
    :rtype: dict
    """

    # extract the file field from the object if omitted
    field = get_field(obj, fieldname)

    # get the value with the fieldmanager
    fm = IFieldManager(field)

    # return None if we have no file data
    if fm.get_size(obj) == 0:
        return None

    out = {
        "content_type": fm.get_content_type(obj),
        "filename": fm.get_filename(obj),
        "download": fm.get_download_url(obj),
        "size": fm.get_size(obj),
    }

    # only return file data only if requested (?filedata=yes)
    if req.get_filedata(False):
        data = fm.get_data(obj)
        out["data"] = data.encode("base64")

    return out


# -----------------------------------------------------------------------------
#   Batching Helpers
# -----------------------------------------------------------------------------

def get_batch(sequence, size, start=0, endpoint=None, complete=False):
    """ create a batched result record out of a sequence (catalog brains)
    """

    batch = make_batch(sequence, size, start)

    return {
        "pagesize": batch.get_pagesize(),
        "next": batch.make_next_url(),
        "previous": batch.make_prev_url(),
        "page": batch.get_pagenumber(),
        "pages": batch.get_numpages(),
        "count": batch.get_sequence_length(),
        "items": make_items_for([b for b in batch.get_batch()],
                                endpoint, complete=complete),
    }


def make_batch(sequence, size=25, start=0):
    """Make a batch of the given size from the sequence
    """
    # we call an adapter here to allow backwards compatibility hooks
    return IBatch(Batch(sequence, size, start))


# -----------------------------------------------------------------------------
#   Functional Helpers
# -----------------------------------------------------------------------------

def fail(status, msg):
    """API Error
    """
    if msg is None:
        msg = "Reason not given."
    raise APIError(status, "{}".format(msg))


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


def get_tool(name, default=_marker):
    """Get a portal tool by name

    :param name: The name of the tool, e.g. `portal_catalog`
    :type name: string
    :returns: Portal Tool
    :rtype: object
    """
    try:
        return ploneapi.portal.get_tool(name)
    except InvalidParameterError:
        if default is not _marker:
            return default
        fail(500, "No tool named '%s' found." % name)


def get_portal_types():
    """Get a list of all portal types

    :retruns: List of portal type names
    :rtype: list
    """
    types_tool = get_tool("portal_types")
    return types_tool.listContentTypes()


def get_resource_mapping():
    """Map resources used in the routes to portal types

    :returns: Mapping of resource->portal_type
    :rtype: dict
    """
    portal_types = get_portal_types()
    resources = map(portal_type_to_resource, portal_types)
    return dict(zip(resources, portal_types))


def portal_type_to_resource(portal_type):
    """Converts a portal type name to a resource name

    :param portal_type: Portal type name
    :type name: string
    :returns: Resource name as it is used in the content route
    :rtype: string
    """
    resource = portal_type.lower()
    resource = resource.replace(" ", "")
    return resource


def resource_to_portal_type(resource):
    """Converts a resource to a portal type

    :param resource: Resource name as it is used in the content route
    :type name: string
    :returns: Portal type name
    :rtype: string
    """
    if resource is None:
        return None

    resource_mapping = get_resource_mapping()
    portal_type = resource_mapping.get(resource.lower())

    # BBB: Handle pre 0.9.1 resource routes, e.g. folders, collections...
    if portal_type is None and resource.endswith("s"):
        new_resource = resource.rstrip("s")
        portal_type = resource_mapping.get(new_resource)
        if portal_type:
            logger.warn("Old style resources will be removed in 1.0. "
                        "Please use '{}' instead of '{}'".format(new_resource, resource))

    if portal_type is None:
        logger.warn("Could not map the resource '{}' "
                    "to any known portal type".format(resource))

    return portal_type


def get_portal_catalog():
    """Get the portal catalog tool

    :returns: Portal Catalog Tool
    :rtype: object
    """
    return get_tool("portal_catalog")


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


def is_at_content(brain_or_object):
    """Checks if the passed in object is an Archetype Content Type

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is an ATCT
    :rtype: bool
    """
    obj = get_object(brain_or_object)
    return IBaseObject.providedBy(obj)


def is_dexterity_content(brain_or_object):
    """Checks if the given object is Dexterity based

    :param obj: The content object to check
    :type thing: ATContentType/DexterityContentType
    :returns: True if the content object is Dexterity based
    :rtype: bool
    """
    obj = get_object(brain_or_object)
    return IDexterityContent.providedBy(obj)


def is_folderish(brain_or_object):
    """Checks if the passed in object is folderish

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: True if the object is folderish
    :rtype: bool
    """
    if hasattr(brain_or_object, "is_folderish"):
        if callable(brain_or_object.is_folderish):
            return brain_or_object.is_folderish()
        return brain_or_object.is_folderish
    return IFolderish.providedBy(get_object(brain_or_object))


def is_uid(uid):
    """Checks if the passed in uid is a valid UID

    :param uid: The uid to check
    :type uid: string
    :return: True if the uid is a valid 32 alphanumeric uid or '0'
    :rtype: bool
    """
    if not isinstance(uid, basestring):
        return False
    if uid != "0" and len(uid) != 32:
        return False
    return True


def is_date(thing):
    """Checks if the given thing represents a date

    :param thing: The object to check if it is a date
    :type thing: arbitrary object
    :returns: True if we have a date object
    :rtype: bool
    """
    # known date types
    date_types = (datetime.datetime,
                  datetime.date,
                  DateTime)
    return isinstance(thing, date_types)


def to_iso_date(date, default=None):
    """ISO representation for the date object

    :param date: A date object
    :type field: datetime/DateTime
    :returns: The ISO format of the date
    :rtype: str
    """

    # not a date
    if not is_date(date):
        return default

    # handle Zope DateTime objects
    if isinstance(date, (DateTime)):
        return date.ISO8601()

    # handle python datetime objects
    return date.isoformat()


def calculate_delta_date(literal):
    """Calculate the date in the past from the given literal

    :param literal: A date literal, e.g. "today"
    :type literal: str
    :returns: Date between the literal and today
    :rtype: DateTime
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


def is_json_serializable(thing):
    """Checks if the given thing can be serialized to JSON

    :param thing: The object to check if it can be serialized
    :type thing: arbitrary object
    :returns: True if it can be JSON serialized
    :rtype: bool
    """
    try:
        json.dumps(thing)
        return True
    except TypeError:
        return False


def to_json_value(obj, fieldname, value=_marker, default=None):
    """JSON save value encoding

    :param obj: Content object
    :type obj: ATContentType/DexterityContentType
    :param fieldname: Schema name of the field
    :type fieldname: str/unicode
    :param value: The field value
    :type value: depends on the field type
    :returns: JSON encoded field value
    :rtype: field dependent
    """

    # This function bridges the value of the field to a probably more complex
    # JSON structure to return to the client.

    # extract the value from the object if omitted
    if value is _marker:
        value = IDataManager(obj).json_data(fieldname)

    # convert objects
    if isinstance(value, ImplicitAcquisitionWrapper):
        return get_url_info(value)

    # convert dates
    if is_date(value):
        return to_iso_date(value)

    # check if the value is callable
    if callable(value):
        value = value()

    # check if the value is JSON serializable
    if not is_json_serializable(value):
        logger.warn("Output {} is not JSON serializable".format(repr(value)))
        return default

    return value


def url_for(endpoint, **values):
    """Looks up the API URL for the given endpoint

    :param endpoint: The name of the registered route
    :type endpoint: string
    :returns: External URL for this endpoint
    :rtype: string/None
    """

    try:
        return router.url_for(endpoint, force_external=True, values=values)
    except Exception:
        # XXX plone.jsonapi.core should catch the BuildError of Werkzeug and
        #     throw another error which can be handled here.
        logger.warn("Could not build API URL for endpoint '%s'. "
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
        return "0"
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


def get_schema(brain_or_object):
    """Get the schema of the content

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Schema object
    """
    obj = get_object(brain_or_object)
    if is_root(obj):
        return None
    if is_dexterity_content(obj):
        pt = get_tool("portal_types")
        fti = pt.getTypeInfo(obj.portal_type)
        return fti.lookupSchema()
    if is_at_content(obj):
        return obj.Schema()
    fail(400, "{} has no Schema.".format(repr(brain_or_object)))


def get_fields(brain_or_object):
    """Get the list of fields from the object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: List of fields
    :rtype: list
    """
    obj = get_object(brain_or_object)
    # The portal object has no schema
    if is_root(obj):
        return {}
    schema = get_schema(obj)
    if is_dexterity_content(obj):
        names = schema.names()
        fields = map(lambda name: schema.get(name), names)
        schema_fields = dict(zip(names, fields))
        # update with behavior fields
        schema_fields.update(get_behaviors(obj))
        return schema_fields
    return dict(zip(schema.keys(), schema.fields()))


def get_field(brain_or_object, name, default=None):
    """Return the named field
    """
    fields = get_fields(brain_or_object)
    return fields.get(name, default)


def get_behaviors(brain_or_object):
    """Iterate over all behaviors that are assigned to the object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Behaviors
    :rtype: list
    """
    obj = get_object(brain_or_object)
    if not is_dexterity_content(obj):
        fail(400, "Only Dexterity contents can have assigned behaviors")
    assignable = IBehaviorAssignable(obj, None)
    if not assignable:
        return {}
    out = {}
    for behavior in assignable.enumerateBehaviors():
        for name, field in getFields(behavior.interface).items():
            out[name] = field
    return out


def get_parent(brain_or_object):
    """Locate the parent object of the content/catalog brain

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: parent object
    :rtype: ATContentType/DexterityContentType/PloneSite/CatalogBrain
    """

    if is_brain(brain_or_object):
        parent_path = get_parent_path(brain_or_object)
        return get_object_by_path(parent_path)

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

    # Nothing to do if the object is contentish
    if not is_folderish(brain_or_object):
        return []

    query = {
        "path": {
            "query": get_path(brain_or_object),
            "depth": depth,
        }
    }

    return search(query=query)


def get_endpoint(brain_or_object, default="plone.jsonapi.routes.get"):
    """Calculate the endpoint for this object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :returns: Endpoint for this object
    :rtype: string
    """
    portal_type = get_portal_type(brain_or_object)
    resource = portal_type_to_resource(portal_type)

    # Try to get the right namespaced endpoint
    endpoints = router.DefaultRouter.view_functions.keys()
    if resource in endpoints:
        return resource  # exact match
    endpoint_candidates = filter(lambda e: e.endswith(resource), endpoints)
    if len(endpoint_candidates) == 1:
        # only return the namespaced endpoint, if we have an exact match
        return endpoint_candidates[0]

    return default


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
    obj = get_object_by_uid(uid, None) or get_object_by_request()

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
    data = req.get_form() or req.get_query_string()
    return get_object_by_record(data)


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


def get_object_by_uid(uid, default=_marker):
    """Find an object by a given UID

    :param uid: The UID of the object to find
    :type uid: string
    :returns: Found Object or None
    """
    if str(uid).lower() in PORTAL_IDS:
        return get_portal()

    # try to find the object with the portal_catalog
    pc = get_portal_catalog()
    res = pc(UID=uid)
    if not res:
        if default is not _marker:
            return default
        fail(404, "No object found for UID {}".format(uid))

    # Catalog should be reindexed if this happens
    if len(res) > 1:
        fail(500, "Found more than one object for UID={}: {}."
             "Please rebuild the catalog or delete the object."
             .format(uid, [r.getPath() for r in res]))

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

    portal = get_portal()
    portal_path = get_path(portal)

    if not path.startswith(portal_path):
        fail(404, "Not a physical path inside the portal")

    if path == portal_path:
        return portal

    try:
        return portal.restrictedTraverse(path)
    except (KeyError, AttributeError):
        return None


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
            fail(400, "Object at %s is not a folder" % curpath)

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
    parent_uid = record.pop("parent_uid", None)
    parent_path = record.pop("parent_path", None)

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
        fail(404, "No target UID/PATH information found")

    if not target:
        fail(404, "No target container found")

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

    # 3. Update sharing settings
    return view.update_role_settings(settings)


def validate_object(brain_or_object, data):
    """Validate the entire object

    :param brain_or_object: A single catalog brain or content object
    :type brain_or_object: ATContentType/DexterityContentType/CatalogBrain
    :param data: The sharing dictionary as returned from the API
    :type data: dict
    :returns: invalidity status
    :rtype: dict
    """
    obj = get_object(brain_or_object)

    # Call the validator of AT Content Types
    if is_at_content(obj):
        return obj.validate(data=data)

    return {}


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
        fail(401, "Removing the Portal is not allowed")
    try:
        return ploneapi.content.delete(obj) is None and True or False
    except Unauthorized:
        fail(401, "Not allowed to delete object '%s'" % obj.getId())


def is_anonymous():
    """Check if the current user is authenticated or not

    :returns: True if the current user is authenticated
    :rtype: bool
    """
    return ploneapi.user.is_anonymous()


def get_current_user():
    """Get the current logged in user

    :returns: Member
    :rtype: object
    """
    return ploneapi.user.get_current()


def get_users():
    """Return all users of the portal.

    :returns: List of Plone Users
    :rtype: object
    """
    acl_users = get_tool("acl_users")
    return acl_users.getUsers()


def get_user(user_or_username=None):
    """Return Plone User

    :param user_or_username: Plone user or user id
    :type groupname:  PloneUser/MemberData/str
    :returns: Plone MemberData
    :rtype: object
    """
    if user_or_username is None:
        return None
    if hasattr(user_or_username, "getUserId"):
        return ploneapi.user.get(user_or_username.getUserId())
    return ploneapi.user.get(userid=u.to_string(user_or_username))


def get_user_properties(user_or_username):
    """Return User Properties

    :param user_or_username: Plone group identifier
    :type groupname:  PloneUser/MemberData/str
    :returns: Plone MemberData
    :rtype: object
    """
    user = get_user(user_or_username)
    if user is None:
        return {}
    if not callable(user.getUser):
        return {}
    out = {}
    plone_user = user.getUser()
    for sheet in plone_user.listPropertysheets():
        ps = plone_user.getPropertysheet(sheet)
        out.update(dict(ps.propertyItems()))
    return out


def get_view(name, context=None, request=None):
    """Get the view by name

    :param name: The name of the view
    :type name: str
    :param context: The context to query the view
    :type context: ATContentType/DexterityContentType/CatalogBrain
    :param request: The request to query the view
    :type request: HTTPRequest object
    :returns: HTTP Request
    :rtype: Products.Five.metaclass View object
    """
    context = context or get_portal()
    request = request or req.get_request() or None
    return getMultiAdapter((get_object(context), request), name=name)


def create_object(container, portal_type, **data):
    """Creates an object slug

    :returns: The new created content object
    :rtype: object
    """

    id = data.pop("id", None)
    title = data.pop("title", None)

    try:
        # create the new object
        obj = ploneapi.content.create(
            container=container,
            type=portal_type,
            id=id,
            title=title)
    except Unauthorized:
        fail(401, "You are not allowed to create this content")

    # Update the object with the given data
    try:
        update_object_with_data(obj, data)
    except APIError:
        # Failure in creation process, delete the invalid object
        container.manage_delObjects(obj.id)
        # reraise the error
        raise

    return obj


def update_object_with_data(content, record):
    """Update the content with the record data

    :param content: A single folderish catalog brain or content object
    :type content: ATContentType/DexterityContentType/CatalogBrain
    :param record: The data to update
    :type record: dict
    :returns: The updated content object
    :rtype: object
    :raises:
        APIError,
        :class:`~plone.jsonapi.routes.exceptions.APIError`
    """

    # ensure we have a full content object
    content = get_object(content)

    # get the proper data manager
    dm = IDataManager(content)

    if dm is None:
        fail(400, "Update for this object is not allowed")

    # https://github.com/collective/plone.jsonapi.routes/issues/77
    # filter out bogus keywords
    # XXX Maybe we should pass only values where we have identical field names?
    field_kwargs = u.omit(record, "file")

    # Iterate through record items
    for k, v in record.items():
        try:
            success = dm.set(k, v, **field_kwargs)
        except Unauthorized:
            fail(401, "Not allowed to set the field '%s'" % k)
        except ValueError, exc:
            fail(400, str(exc))

        if not success:
            logger.warn("update_object_with_data::skipping key=%r", k)
            continue

        logger.debug("update_object_with_data::field %r updated", k)

    # Validate the entire content object
    invalid = validate_object(content, record)
    if invalid:
        fail(400, u.to_json(invalid))

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
