# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging
import datetime
import DateTime

import simplejson as json

from zope import interface
from zope import component

from plone import api

from plone.dexterity.schema import SCHEMA_CACHE
from plone.dexterity.interfaces import IDexterityContent

from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ATContentTypes.interfaces import IATContentType

from plone.jsonapi.routes.interfaces import IInfo

logger = logging.getLogger("plone.jsonapi.routes")


class Base(object):
    """ Base Adapter
    """
    interface.implements(IInfo)

    def __init__(self, context):
        self.context = context
        self.keys = []

    def to_dict(self):
        return to_dict(self.context, keys=self.keys)

    def __call__(self):
        return self.to_dict()


class ZCDataProvider(Base):
    """ Catalog Brain Adapter
    """
    interface.implements(IInfo)
    component.adapts(ICatalogBrain)

    def __init__(self, context):
        super(self.__class__, self).__init__(context)

    def to_dict(self):
        brain = self.context
        return {
            "id":          brain.getId,
            "uid":         brain.UID,
            "title":       brain.Title,
            "description": brain.Description,
            "url":         brain.getURL(),
            "portal_type": brain.portal_type,
            "created":     brain.created.ISO8601(),
            "modified":    brain.modified.ISO8601(),
            "effective":   brain.effective.ISO8601(),
            "type":        brain.portal_type,
            "tags":        brain.Subject,
        }


class DexterityDataProvider(Base):
    """ Data Provider for Dexterity based content types
    """
    interface.implements(IInfo)
    component.adapts(IDexterityContent)

    def __init__(self, context):
        super(self.__class__, self).__init__(context)

        schema = SCHEMA_CACHE.get(context.portal_type)
        self.keys = schema.names()


class ATDataProvider(Base):
    """ Archetypes Adapter
    """
    interface.implements(IInfo)
    component.adapts(IATContentType)

    def __init__(self, context):
        super(self.__class__, self).__init__(context)
        schema = context.Schema()
        self.keys = schema.keys()

#---------------------------------------------------------------------------
#   Functional Helpers
#---------------------------------------------------------------------------

def to_dict(obj, keys):
    """ returns a dictionary of the given keys
    """
    out = dict()
    for key in keys:
        field = get_field(obj, key)
        out[key] = get_value(field)
    if out.get("workflow_info"):
        logger.warn("Workflow Info ommitted since the key 'workflow_info' was ",
                "found in the current schema")
        return out
    out["workflow_info"] = get_wf_info(obj)
    return out


def get_field(obj, key):
    """ get the value for the given key
        => handles Dexterity/AT Content types
    """
    if IATContentType.providedBy(obj):
        return obj.getField(key).getAccessor(obj)()
    return getattr(obj, key)


def get_value(field):
    """ extract the value from the given field
    """

    if isinstance(field, (datetime.datetime, datetime.date, DateTime.DateTime)):
        return get_iso_date(field)

    if hasattr(field, "filename"):
        return get_file_dict(field)

    if not is_json_serializable(field):
        return None

    return field


def get_file_dict(field):
    """ file representation of the given data
    """
    return {
        "data": field.data.encode("base64"),
        "size": len(field.data),
        "content_type": getattr(field, "content_type", "application/octet-stream"),
    }


def get_iso_date(date=None):
    """ get the iso string for python datetime objects
    """
    if date is None:
        return ""

    if isinstance(date, (DateTime.DateTime)):
        return date.ISO8601()

    return date.isoformat()


def is_json_serializable(thing):
    """ checks if the given thing can be serialized to json
    """
    try:
        json.dumps(thing)
        return True
    except TypeError:
        return False


def get_wf_info(obj):
    """ returns the workflow information of the first assigned workflow
    """

    # get the portal workflow tool
    wf_tool = api.portal.get_tool("portal_workflow")

    # the assigned workflows of this object
    wfs = wf_tool.getWorkflowsFor(obj)

    # no worfkflows assigned -> return
    if not wfs: return {}

    # get the first one
    workflow = wfs[0]

    # get the status info of the current state (dictionary)
    status = wf_tool.getStatusOf(workflow.getId(), obj)

    # get the current review_status
    current_state_id = status.get("review_state", None)

    # get the wf status object
    current_status = workflow.states[current_state_id]

    # get the title of the current status
    current_state_title = current_status.title

    # get the transition informations
    transitions = map(to_transition_info, wf_tool.getTransitionsFor(obj))

    return {
        "workflow":     workflow.getId(),
        "status":       current_state_title,
        "review_state": current_state_id,
        "transitions":  transitions
    }


def to_transition_info(transition):
    """ return the transition information
    """
    return {
        "value":   transition["id"],
        "display": transition["description"],
        "url":     transition["url"],
    }


def to_iso_date(date=None):
    """ get the iso string for python datetime objects
    """
    if date is None:
        return ""
    return date.isoformat()

# vim: set ft=python ts=4 sw=4 expandtab :
