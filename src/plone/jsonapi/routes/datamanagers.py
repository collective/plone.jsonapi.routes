# -*- coding: utf-8 -*-

import logging

from zope import interface
from zope.schema import getFields
from zope.schema.interfaces import IObject

from plone import api
from plone.behavior.interfaces import IBehaviorAssignable

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore import permissions
from Products.Archetypes.utils import mapply

from plone.jsonapi.routes.interfaces import IDataManager

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

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
            logger.debug("ATDataManager::set:File field detected ('%r'), base64 decoding value", field)
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
        logger.debug("ATDataManager::set: field=%r, value=%r", field, value)
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
        self.behaviors = self.get_behaviors()

    def get_behaviors(self):
        """ Iterate over all behaviors that are assigned to the object
        Used code from @tisto:
        https://github.com/plone/plone.restapi/blob/master/src/plone/restapi/utils.py
        """
        out = {}
        assignable = IBehaviorAssignable(self.context, None)
        if not assignable: return out
        for behavior in assignable.enumerateBehaviors():
            for name, field in getFields(behavior.interface).items():
                out[name] = field
        return out

    def get_schema(self):
        pt = api.portal.get_tool("portal_types")
        fti = pt.getTypeInfo(self.context.portal_type)
        return fti.lookupSchema()

    def get_field(self, name):
        sf = self.schema.get(name)
        bf = self.behaviors.get(name)
        return sf or bf

    def is_file_field(self, field):
        """ checks if field is a file field
        """
        return IObject.providedBy(field)

    def set(self, name, value, **kw):
        """ Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return False

        # check if the field is read only
        if field.readonly:
            raise Unauthorized("Field '%s' is read-only" % name)

        # XXX: How to check security on the field level?
        sm = getSecurityManager()
        if not sm.checkPermission(permissions.ModifyPortalContent, self.context):
            raise Unauthorized("You are not allowed to modify this content")

        if self.is_file_field(field):
            logger.debug("DexterityDataManager::set:File field detected ('%r'), base64 decoding value", field)
            data = str(value).decode("base64")
            if "filename" not in kw:
                logger.debug("ATDataManager::set:No Filename detected -- using title or id")
                kw["filename"] = kw.get("id") or kw.get("title")
            value = field._type(data=data, filename=kw.get("filename"))

        logger.debug("DexterityDataManager::set: field=%r, value=%r", field, value)
        field.set(self.context, value)
        return True

    def get(self, name):
        """ get the value of the field by name
        """
        field = self.get_field(name)
        # XXX: How to check security on the field level?
        sm = getSecurityManager()
        if not sm.checkPermission(permissions.View, self.context):
            raise Unauthorized("You are not allowed to view this content")
        return field.get(self.context)
