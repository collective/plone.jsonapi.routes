# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import datetime
import DateTime

import simplejson as json

from zope import interface
from zope import component

from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ATContentTypes.interfaces import IATContentType
from plone.jsonapi.routes.interfaces import IInfo


class Base(object):
    """ Base Adapter
    """
    interface.implements(IInfo)

    def __init__(self, context):
        self.context = context
        self.keys = []

    def to_dict(self):
        return get_info(self.context, keys=self.keys)

    def __call__(self):
        return self.to_dict()


class ZCInfo(Base):
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
            "tags":        brain.subject,
        }


class ATInfo(Base):
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

def get_info(obj, keys):
    """ returns a dictionary of the given keys
    """

    out = dict()
    for key in keys:
        # get the schema field
        field = obj.getField(key)
        if field is None:
            continue

        # extract the value
        value = field.getAccessor(obj)()

        # XXX - use adapters here

        # handle dates
        if isinstance(value, (datetime.datetime, datetime.date, DateTime.DateTime)):
            value = to_iso_date(value)

        if hasattr(value, "filename"):
            value = value.data.encode("base64")

        try:
            json.dumps(value)
        except TypeError:
            continue

        out[key] = value
    return out


def to_iso_date(date=None):
    """ get the iso string for python datetime objects
    """
    if date is None:
        return ""

    if isinstance(date, (DateTime.DateTime)):
        return date.ISO8601()

    return date.isoformat()

# vim: set ft=python ts=4 sw=4 expandtab :
