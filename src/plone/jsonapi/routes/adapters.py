# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

from zope import interface
from zope import component

from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.interfaces import IATDocument

from interfaces import IInfo


class BaseInfo(object):
    """ Base Adapter
    """
    interface.implements(IInfo)
    component.adapts(IATContentType)

    def __init__(self, context):
        self.context = context

    def to_dict(self, obj):
        return {
            "created":   obj.created().ISO8601(),
            "modified":  obj.modified().ISO8601(),
            "effective": obj.effective().ISO8601(),
        }

    def __call__(self):
        return self.to_dict(self.context)


class DocumentInfo(BaseInfo):
    """ Document Adapter
    """
    interface.implements(IInfo)
    component.adapts(IATDocument)

    def to_dict(self, obj):
        out = super(DocumentInfo, self).to_dict(obj)
        out.update({
            "text": obj.getText()
        })
        return out


# vim: set ft=python ts=4 sw=4 expandtab :
