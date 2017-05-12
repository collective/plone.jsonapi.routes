# -*- coding: utf-8 -*-

from zope import interface

from AccessControl import Unauthorized
from AccessControl import getSecurityManager

from Products.CMFCore import permissions

from plone.jsonapi.routes import api
from plone.jsonapi.routes import logger
from plone.jsonapi.routes.interfaces import IDataManager
from plone.jsonapi.routes.interfaces import IFieldManager

__author__ = 'Ramon Bartl <rb@ridingbytes.com>'
__docformat__ = 'plaintext'


class BrainDataManager(object):
    """ Adapter to get catalog brain attributes
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get(self, name):
        """ get the value by name
        """
        # read the attribute
        attr = getattr(self.context, name, None)
        if callable(attr):
            return attr()
        return attr

    def set(self, name, value, **kw):
        """ Not used for catalog brains
        """
        logger.warn("set attributes not allowed on catalog brains")


class PortalDataManager(object):
    """ Adapter to set and get attributes of the Plone portal
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get(self, name):
        """ get the value by name
        """

        # check read permission
        sm = getSecurityManager()
        permission = permissions.View
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to view the Plone portal")

        # read the attribute
        attr = getattr(self.context, name, None)
        if callable(attr):
            return attr()

        # XXX no really nice, but we want the portal to behave like an ordinary
        # content type. Therefore we need to inject the neccessary data.
        if name == "uid":
            return "0"
        if name == "path":
            return "/%s" % self.context.getId()
        return attr

    def set(self, name, value, **kw):
        """ Set the attribute to the given value.

        The keyword arguments represent the other attribute values
        to integrate constraints to other values.
        """

        # check write permission
        sm = getSecurityManager()
        permission = permissions.ManagePortal
        if not sm.checkPermission(permission, self.context):
            raise Unauthorized("Not allowed to modify the Plone portal")

        # set the attribute
        if not hasattr(self.context, name):
            return False
        self.context[name] = value
        return True


class ATDataManager(object):
    """ Adapter to set and get field values of AT Content Types
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context

    def get_field(self, name):
        """ return the field by name
        """
        return self.context.getField(name)

    def set(self, name, value, **kw):
        """ Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """

        # fetch the field by name
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return False

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.set(self.context, value, **kw)

    def get(self, name):
        """ get the value of the field by name
        """

        # fetch the field by name
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return None

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.get(self.context)


class DexterityDataManager(object):
    """ Adapter to set and get field values of Dexterity Content Types
    """
    interface.implements(IDataManager)

    def __init__(self, context):
        self.context = context
        self.schema = api.get_schema(context)
        self.behaviors = api.get_behaviors(context)

    def get_field(self, name):
        """Return the field
        """
        sf = self.schema.get(name)
        bf = self.behaviors.get(name)
        return sf or bf

    def set(self, name, value, **kw):
        """Set the field to the given value.

        The keyword arguments represent the other field values
        to integrate constraints to other values.
        """

        # fetch the field by name
        field = self.get_field(name)

        # bail out if we have no field
        if not field:
            return False

        # Check the write permission of the context
        # XXX: This should be done on field level by the field manager adapter
        if not self.can_write():
            raise Unauthorized("You are not allowed to modify this content")

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.set(self.context, value, **kw)

    def get(self, name):
        """Get the value of the field by name
        """

        # fetch the field by name
        field = self.get_field(name)

        # Check the read permission of the context
        # XXX: This should be done on field level by the field manager adapter
        if not self.can_write():
            raise Unauthorized("You are not allowed to modify this content")

        # bail out if we have no field
        if field is None:
            return None

        # call the field adapter and set the value
        fieldmanager = IFieldManager(field)
        return fieldmanager.get(self.context)

    def can_write(self):
        """Check if the field is writeable
        """
        sm = getSecurityManager()
        permission = permissions.ModifyPortalContent

        if not sm.checkPermission(permission, self.context):
            return False
        return True

    def can_read(self):
        """Check if the field is readable
        """
        sm = getSecurityManager()
        if not sm.checkPermission(permissions.View, self.context):
            return False
        return True
