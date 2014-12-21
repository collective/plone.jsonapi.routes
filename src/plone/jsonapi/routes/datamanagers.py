# -*- coding: utf-8 -*-

__author__    = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import logging

from zope import interface

from plone import api

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
        if field.__name__ in ["file", "image"]:
            return True
        return False

    def get_field(self, name):
        return self.context.getField(name)

    def set(self, name, value):
        field = self.get_field(name)
        logger.info("ATDataManager::set: name=%r, value=%r, field=%r", name, value, field)
        if not field:
            return False
        if self.is_file_field(field):
            logger.info("ATDataManager::set:File field detected ('%r'), base64 decoding value", field)
            value = str(value).decode("base64")
        mutator = field.getMutator(self.context)
        mutator(value)
        return True

    def get(self, name):
        field = self.get_field(name)
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
