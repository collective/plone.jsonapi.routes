# -*- coding: utf-8 -*-

import logging
import mimetypes
import datetime
import DateTime
import Missing

import simplejson as json

from zope import interface
from zope import component

from plone.dexterity.schema import SCHEMA_CACHE
from plone.dexterity.interfaces import IDexterityContent

from AccessControl import Unauthorized

from Products.CMFCore.interfaces import ISiteRoot
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.ATContentTypes.interfaces import IATContentType

from plone.jsonapi.routes.interfaces import IInfo
from plone.jsonapi.routes.interfaces import IDataManager
from plone.jsonapi.routes import api
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
            "author":      "Creator",
        }

    def to_dict(self):
        """ extract the data of the content and return it as a dictionary
        """

        # 1. extract the schema fields
        data = extract_fields(self.context, self.keys, ignore=self.ignore)

        # 2. include custom key-value pairs listed in the mapping dictionary
        for key, attr in self.attributes.iteritems():
            # key already extracted in the first step
            if data.get(key, _marker) is not _marker:
                continue  # don't overwrite
            if key in self.ignore:
                continue  # skip ignores
            # fetch the mapped attribute
            value = getattr(self.context, attr, None)
            # handle function calls
            if callable(value):
                value = value()
            # map the value to the given key from the mapping
            data[key] = get_json_value(self.context, key, value)
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
        catalog = api.get_portal_catalog()
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

def extract_fields(obj, fieldnames, ignore=[]):
    """Extract the given fieldnames from the object

    :param obj: Content object
    :type obj: ATContentType/DexterityContentType
    :param ignore: Schema names to ignore
    :type ignore: list
    :returns: Schema name/value mapping
    :rtype: dict
    """

    # get the proper data manager for the object
    dm = IDataManager(obj)

    # filter out ignored fields
    fieldnames = filter(lambda name: name not in ignore, fieldnames)

    # schema mapping
    out = dict()

    for fieldname in fieldnames:
        try:
            # get the field value with the data manager
            fieldvalue = dm.get(fieldname)
        # https://github.com/collective/plone.jsonapi.routes/issues/52
        # -> skip restricted fields
        except Unauthorized:
            logger.debug("Skipping restricted field '%s'" % fieldname)
            continue
        out[fieldname] = get_json_value(obj, fieldname, fieldvalue)

    return out


def get_json_value(obj, fieldname, value=_marker, default=None):
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

    # returned from catalog brain metadata
    if value is Missing.Value:
        return default

    # extract the value from the object if omitted
    if value is _marker:
        value = IDataManager(obj).get(fieldname)

    # check if we have a date
    if is_date(value):
        return get_iso_date(value)

    # check if the value is a file field
    if is_file_field(value):

        # Issue https://github.com/collective/plone.jsonapi.routes/issues/54
        # -> return file data only if requested
        if req.get_filedata(False):
            return get_file_info(obj, fieldname, value)

        # return the donwload url as the default file field value
        value = get_download_url(obj, fieldname, value)

    # check if the value is JSON serializable
    if not is_json_serializable(value):
        return default

    return value


def get_file_info(obj, fieldname, field=_marker, default=None):
    """Extract file data from a file field

    :param obj: Content object
    :type obj: ATContentType/DexterityContentType
    :param fieldname: Schema name of the field
    :type fieldname: str/unicode
    :param field: Blob field
    :type field: plone.app.blob.field.BlobWrapper
    :returns: File data mapping
    :rtype: dict
    """

    # extract the file field from the object if omitted
    if field is _marker:
        field = IDataManager(obj).get(fieldname)

    # check if we have a file field
    if not is_file_field(field):
        return default

    # extract file field attributes
    data = field.data.encode("base64")
    content_type = get_content_type(field)
    filename = getattr(field, "filename", "")
    download = get_download_url(obj, fieldname, field)

    return {
        "data": data,
        "size": len(field.data),
        "content_type": content_type,
        "filename": filename,
        "download": download,
    }


def get_download_url(obj, fieldname, field=_marker, default=None):
    """Calculate the download url

    :param obj: Content object
    :type obj: ATContentType/DexterityContentType
    :param fieldname: Schema name of the field
    :type fieldname: str/unicode
    :param field: The file field
    :type field: object
    :returns: The file download url
    :rtype: str
    """

    # extract the file field from the object if omitted
    if field is _marker:
        field = IDataManager(obj).get(fieldname)

    # check if we have a file field
    if not is_file_field(field):
        return default

    download = None
    if is_dexterity_content(obj):
        # calculate the download url
        filename = getattr(field, "filename", "")
        download = "{}/@@download/{}/{}".format(
            obj.absolute_url(), fieldname, filename)
    else:
        # calculate the download url
        download = "{}/download".format(obj.absolute_url())
    return download


def get_content_type(obj, default="application/octet-stream"):
    """Get the content type of the file object

    :param obj: ATContentType, DexterityContentType, BlobWrapper
    :type obj: object
    :returns: The content type of the file
    :rtype: str
    """
    if hasattr(obj, "contentType"):
        return obj.contentType
    elif hasattr(obj, "content_type"):
        return obj.content_type
    filename = getattr(obj, "filename", "")
    content_type = mimetypes.guess_type(filename)[0]
    return content_type or default


def get_iso_date(date, default=None):
    """Get the ISO representation for the date object

    :param date: A date object
    :type field: datetime/DateTime
    :returns: The ISO format of the date
    :rtype: str
    """

    # not a date
    if not is_date(date):
        return default

    # handle Zope DateTime objects
    if isinstance(date, (DateTime.DateTime)):
        return date.ISO8601()

    # handle python datetime objects
    return date.isoformat()


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
                  DateTime.DateTime)
    return isinstance(thing, date_types)


def is_dexterity_content(obj):
    """Checks if the given object is Dexterity based

    :param obj: The content object to check
    :type thing: ATContentType/DexterityContentType
    :returns: True if the content object is Dexterity based
    :rtype: bool
    """
    return IDexterityContent.providedBy(obj)


def is_file_field(field):
    """Checks if the field is a file field

    :param field: The field to test
    :type thing: field object
    :returns: True if the field is a file field
    :rtype: bool
    """
    return hasattr(field, "filename")
