# -*- coding: utf-8 -*-

from zope import interface

from DateTime import DateTime

from AccessControl import Unauthorized

from Products.Archetypes.utils import mapply

from plone.jsonapi.routes import logger
from plone.jsonapi.routes import api
from plone.jsonapi.routes import underscore as u
from plone.jsonapi.routes.interfaces import IFieldManager


class ZopeSchemaFieldManager(object):
    """Adapter to get/set the value of Zope Schema Fields
    """
    interface.implements(IFieldManager)

    def __init__(self, field):
        self.field = field

    def get(self, instance, **kw):
        """Get the value of the field
        """
        return self._get(instance, **kw)

    def set(self, instance, value, **kw):
        """Set the value of the field
        """
        return self._set(instance, value, **kw)

    def _set(self, instance, value, **kw):
        """Set the value of the field
        """
        logger.debug("DexterityFieldManager::set: value=%r" % value)

        # Check if the field is read only
        if self.field.readonly:
            raise Unauthorized("Field is read only")

        # Validate
        self.field.validate(value)

        # TODO: Check security on the field level
        return self.field.set(instance, value)

    def _get(self, instance, **kw):
        """Get the value of the field
        """
        logger.debug("DexterityFieldManager::get: instance={} field={}"
                     .format(instance, self.field))

        # TODO: Check security on the field level
        return self.field.get(instance)


class RichTextFieldManager(ZopeSchemaFieldManager):
    """Adapter to get/set the value of Rich Text Fields
    """
    interface.implements(IFieldManager)

    def set(self, instance, value, **kw):
        from plone.app.textfield.value import RichTextValue
        value = RichTextValue(raw=value,
                              outputMimeType=self.field.output_mime_type)
        return self._set(instance, value, **kw)


class NamedFileFieldManager(ZopeSchemaFieldManager):
    """Adapter to get/set the value of Named File Fields
    """
    interface.implements(IFieldManager)

    def set(self, instance, value, **kw):
        logger.debug("NamedFileFieldManager::set:File field"
                     "detected ('%r'), base64 decoding value", self.field)
        data = str(value).decode("base64")
        filename = self.get_filename(**kw)
        contentType = self.get_content_type(**kw)

        if contentType:
            # create NamedFile with content type information
            value = self.field._type(data=data,
                                     contentType=contentType,
                                     filename=filename)
        else:
            # create NamedFile w/o content type information
            # -> will be guessed by the extension of the filename
            value = self.field._type(data=data, filename=filename)

        return self.field.set(instance, value)

    def get_filename(self, **kw):
        """Extract the filename from the keywords
        """
        if "filename" not in kw:
            logger.debug("NamedFileFieldManager::get_filename:No Filename detected"
                         "-- using title or id")
            kw["filename"] = kw.get("id") or kw.get("title")
        return kw.get("filename")

    def get_content_type(self, **kw):
        """Extract the mimetype from the keywords
        """
        if "mimetype" in kw:
            return kw.get("mimetype")
        if "content_type" in kw:
            # same key as in JSON response
            return kw.get("content_type")
        return None


class NamedImageFieldManager(NamedFileFieldManager):
    """Adapter to get/set the value of Named Image Fields
    """
    interface.implements(IFieldManager)


class ATFieldManager(object):
    """Adapter to get/set the value of AT Fields
    """
    interface.implements(IFieldManager)

    def __init__(self, field):
        self.field = field
        self.name = field.getName()

    def get_field(self):
        """Get the adapted field
        """
        return self.field

    def get(self, instance, **kw):
        """Get the value of the field
        """
        return self._get(instance, **kw)

    def set(self, instance, value, **kw):
        """Set the value of the field
        """
        return self._set(instance, value, **kw)

    def _set(self, instance, value, **kw):
        """Set the value of the field
        """
        logger.debug("ATFieldManager::set: value=%r" % value)

        # check field permission
        if not self.field.checkPermission("write", instance):
            raise Unauthorized("You are not allowed to write the field {}"
                               .format(self.name))

        # check if field is writable
        if not self.field.writeable(instance):
            raise Unauthorized("Field {} is read only."
                               .format(self.name))

        # id fields take only strings
        if self.name == "id":
            value = str(value)

        # get the field mutator
        mutator = self.field.getMutator(instance)

        # Inspect function and apply *args and **kwargs if possible.
        mapply(mutator, value, **kw)

        return True

    def _get(self, instance, **kw):
        """Get the value of the field
        """
        logger.debug("ATFieldManager::get: instance={} field={}"
                     .format(instance, self.field))

        # check the field permission
        if not self.field.checkPermission("read", instance):
            raise Unauthorized("You are not allowed to read the field {}"
                               .format(self.name))

        # return the field value
        return self.field.get(instance)


class TextFieldManager(ATFieldManager):
    """Adapter to get/set the value of Text Fields
    """
    interface.implements(IFieldManager)


class DateTimeFieldManager(ATFieldManager):
    """Adapter to get/set the value of DateTime Fields
    """
    interface.implements(IFieldManager)

    def set(self, instance, value, **kw):
        """Converts the value into a DateTime object before setting.
        """
        try:
            value = DateTime(value)
        except SyntaxError:
            logger.warn("Value '{}' is not a valid DateTime string"
                        .format(value))
            return False

        self._set(instance, value, **kw)


class FileFieldManager(ATFieldManager):
    """Adapter to get/set the value of File Fields
    """
    interface.implements(IFieldManager)

    def set(self, instance, value, **kw):
        """Decodes base64 value and set the file object
        """
        value = str(value).decode("base64")

        # handle the filename
        if "filename" not in kw:
            logger.debug("FielFieldManager::set: No Filename detected "
                         "-> using title or id")
            kw["filename"] = kw.get("id") or kw.get("title")

        self._set(instance, value, **kw)


class ReferenceFieldManager(ATFieldManager):
    """Adapter to get/set the value of Reference Fields
    """
    interface.implements(IFieldManager)

    def __init__(self, field):
        super(ReferenceFieldManager, self).__init__(field)
        self.allowed_types = field.allowed_types
        self.multi_valued = field.multiValued

    def is_multi_valued(self):
        return self.multi_valued

    def set(self, instance, value, **kw):  # noqa
        """Set the value of the refernce field
        """
        ref = []

        # The value is an UID
        if api.is_uid(value):
            ref.append(api.get_object_by_uid(value))

        # The value is already an object
        if api.is_at_content(value):
            ref.append(value)

        # The value is a dictionary
        # -> handle it like a catalog query
        if u.is_dict(value):
            results = api.search(portal_type=self.allowed_types, **value)
            ref = map(api.get_object, results)

        # The value is a list
        if u.is_list(value):
            for item in value:
                # uid
                if api.is_uid(item):
                    ref.append(api.get_object_by_uid(item))
                    continue

                # object
                if api.is_at_content(item):
                    ref.append(api.get_object(item))
                    continue

                # path
                if api.is_path(item):
                    ref.append(api.get_object_by_path(item))
                    continue

                # dict (catalog query)
                if u.is_dict(item):
                    results = api.search(portal_type=self.allowed_types, **item)
                    objs = map(api.get_object, results)
                    ref.extend(objs)
                    continue

                # Plain string
                # -> do a catalog query for title
                if isinstance(item, basestring):
                    results = api.search(portal_type=self.allowed_types, title=item)
                    objs = map(api.get_object, results)
                    ref.extend(objs)
                    continue

        # The value is a physical path
        if api.is_path(value):
            ref = api.get_object_by_path(value)

        # Handle non multi valued fields
        if not self.multi_valued and len(ref) > 1:
            raise ValueError("Multiple values given for single valued field {}"
                             .format(self.field))

        return self._set(instance, ref, **kw)
