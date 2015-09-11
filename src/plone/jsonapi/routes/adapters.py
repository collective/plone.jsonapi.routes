# -*- coding: utf-8 -*-

import logging
import datetime
import DateTime
import Missing

import simplejson as json

from zope import interface
from zope import component

from plone import api

from plone.dexterity.schema import SCHEMA_CACHE
from plone.dexterity.interfaces import IDexterityContent

from AccessControl import Unauthorized

from Products.CMFCore.interfaces import ISiteRoot
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ATContentTypes.interfaces import IATContentType

from plone.jsonapi.routes.interfaces import IInfo
from plone.jsonapi.routes.interfaces import IDataManager
from plone.jsonapi.routes import request as req

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

_marker = object

logger = logging.getLogger("plone.jsonapi.routes")


class Base(object):
    """ Base Adapter
    """
    interface.implements(IInfo)

    def __init__(self, context):
        self.context = context
        self.keys = []
        self.ignore = []

        # Mapped attributes to extract from the object besides the schema keys.
        # These keys are always included
        self.attributes = {
            "id":          "getId",
            "uid":         "UID",
            "title":       "Title",
            "description": "Description",
            "created":     "created",
            "modified":    "modified",
            "effective":   "effective",
            "portal_type": "portal_type",
            "tags":        "Subject",
        }

    def to_dict(self):
        """ extract the data of the content and return it as a dictionary
        """

        # 1. extract the schema keys
        data = extract_keys(self.context, keys=self.keys, ignore=self.ignore)

        # 2. include custom key-value pairs listed in the mapping dictionary
        for key, attr in self.attributes.iteritems():
            # key already extracted in the first step
            if data.get(key):
                continue  # don't overwrite
            if key in self.ignore:
                continue  # skip ignores
            # fetch the mapped attribute
            value = getattr(self.context, attr, None)
            # handle function calls
            if callable(value):
                value = value()
            # map the value to the given key from the mapping
            data[key] = get_json_value(self.context, key, value=value)
        return data

    def __call__(self):
        return self.to_dict()


class ZCDataProvider(Base):
    """ Catalog Brain Adapter
    """
    interface.implements(IInfo)
    component.adapts(ICatalogBrain)

    def __init__(self, context):
        super(ZCDataProvider, self).__init__(context)
        catalog = api.portal.get_tool("portal_catalog")
        # extract the metadata
        self.keys = catalog.schema()

        # add specific catalog brain mappings
        self.attributes.update({
            "path": "getPath",
        })

        # ignore some metadata values, which we already mapped
        self.ignore = [
            'CreationDate',
            'Creator',
            'Date',
            'Description',
            'EffectiveDate',
            'ExpirationDate',
            'ModificationDate',
            'Subject',
            'Title',
            'Type',
            'UID',
            'cmf_uid',
            'getIcon',
            'getId',
            'getObjSize',
            'getRemoteUrl',
            'listCreators',
            'meta_type',
        ]


class DexterityDataProvider(Base):
    """ Data Provider for Dexterity based content types
    """
    interface.implements(IInfo)
    component.adapts(IDexterityContent)

    def __init__(self, context):
        super(DexterityDataProvider, self).__init__(context)

        schema = SCHEMA_CACHE.get(context.portal_type)
        self.keys = schema.names()


class ATDataProvider(Base):
    """ Archetypes Adapter
    """
    interface.implements(IInfo)
    component.adapts(IATContentType)

    def __init__(self, context):
        super(ATDataProvider, self).__init__(context)
        schema = context.Schema()
        self.keys = schema.keys()


class SiteRootDataProvider(Base):
    """ Site Root Adapter
    """
    interface.implements(IInfo)
    component.adapts(ISiteRoot)

    def __init__(self, context):
        super(SiteRootDataProvider, self).__init__(context)
        # virtual keys, which are handled by the data manager
        self.keys = ["uid", "path"]


# ---------------------------------------------------------------------------
#   Functional Helpers
# ---------------------------------------------------------------------------

def extract_keys(obj, keys, ignore=[]):
    """ fetch the given keys from the object using the proper data manager
    """
    # see interfaces.IDataManager
    dm = IDataManager(obj)

    # filter out ignores
    keys = filter(lambda key: key not in ignore, keys)
    out = dict()

    for key in keys:
        try:
            # get the field value with the data manager
            value = dm.get(key)
        # https://github.com/collective/plone.jsonapi.routes/issues/52
        # -> skip restricted fields
        except Unauthorized:
            logger.debug("Skipping restricted field '%s'" % key)
            continue
        out[key] = get_json_value(obj, key, value=value)

    return out


def get_json_value(obj, key, value=None):
    """ json save value encoding
    """

    # returned from catalog brain metadata
    if value is Missing.Value:
        return None

    # extract the value from the object if omitted
    if value is None:
        value = IDataManager(obj).get(key)

    # known date types
    date_types = (datetime.datetime,
                  datetime.date,
                  DateTime.DateTime)

    # check if we have a date
    if isinstance(value, date_types):
        return get_iso_date(value)

    # check if the value is a file object
    if hasattr(value, "filename"):
        # => value is e.g. a named blob file
        return get_file_dict(obj, key, value=value)

    if not is_json_serializable(value):
        return None

    return value


def get_file_dict(obj, key, value=None):
    """ file representation of the given data
    """

    # extract the value from the object if omitted
    if value is None:
        value = IDataManager(obj).get(key)

    # extract file attributes
    data = value.data.encode("base64")
    content_type = get_content_type(value)
    filename = getattr(value, "filename", "")
    download = None

    if IDexterityContent.providedBy(obj):
        # calculate the download url
        download = "{}/@@download/{}/{}".format(
            obj.absolute_url(), key, filename)
    else:
        # calculate the download url
        download = "{}/download".format(obj.absolute_url())

    return {
        "data": data,
        "size": len(value.data),
        "content_type": content_type,
        "filename": filename,
        "download": download,
    }


def get_content_type(fileobj):
    """ get the content type of the file object
    """
    if hasattr(fileobj, "contentType"):
        return fileobj.contentType
    return getattr(fileobj, "content_type", "application/octet-stream")


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
