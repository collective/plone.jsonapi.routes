# -*- coding: utf-8 -*-

__author__    = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import interface

from plone import api

from AccessControl import Unauthorized
from Products.Archetypes.utils import mapply

from plone.jsonapi.routes.interfaces import IDataManager

logger = logging.getLogger("plone.jsonapi.routes.datamanagers")


class ATDataManager(object):
    """ Adapter to set and get field values of AT Content Types
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def is_file_field(self, field):
        """ checks if field is a file field
        """
        # XXX find a better way to distinguish file/image fields
        if getattr(field, "type", None) in ["file", "image", "blob"]:
            return True
        return False

    def get_field(self, name):
        """ return the field by name
        """
        return self.context.getField(name)

    def set(self, name, value, **kw):
        """ Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return False
        # check the field permission
        if not field.checkPermission("write", self.context):
            raise Unauthorized("You are not allowed to write the field %s" % name)
        if self.is_file_field(field):
            logger.info("ATDataManager::set:File field detected ('%r'), base64 decoding value", field)
            value = str(value).decode("base64")
            # handle the filename
            if "filename" not in kw:
                logger.debug("ATDataManager::set:No Filename detected -- using title or id")
                kw["filename"] = kw.get("id") or kw.get("title")

        # set the value to the field
        self._set(field, value, **kw)
        return True

    def _set(self, field, value, **kw):
        """ set the raw value of the field
        """
        logger.info("ATDataManager::set: field=%r, value=%r", field, value)
        # get the field mutator
        mutator = field.getMutator(self.context)
        # Inspect function and apply positional and keyword arguments as possible.
        return mapply(mutator, value, **kw)

    def get(self, name):
        """ get the value of the field by name
        """
        field = self.get_field(name)
        if not field.checkPermission("read", self.context):
            raise Unauthorized("You are not allowed to read the field %s" % name)
        return field.get(self.context)


class DexterityDataManager(object):
    """ Adapter to set and get field values of Dexterity Content Types
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context
        self.schema = self.get_schema()

    def get_schema(self):
        pt = api.portal.get_tool("portal_types")
        fti = pt.getTypeInfo(self.context.portal_type)
        return fti.lookupSchema()

    def get_field(self, name):
        return self.schema.get(name)

    def set(self, name, value):
        field = self.get_field(name)
        logger.info("DexterityDataManager::set: name=%r, value=%r, field=%r", name, value, field)
        field.set(self.context, value)

    def get(self, name):
        field = self.get_field(name)
        return field.get(self.context)

# vim: set ft=python ts=4 sw=4 expandtab :
