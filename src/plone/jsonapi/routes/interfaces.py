# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.de>'
__docformat__ = 'plaintext'

from zope import interface


class IDataManager(interface.Interface):
    """ Field Interface
    """

    def get(name):
        """ Get the value of the named field with
        """

    def set(name, value):
        """ Set the value of the named field
        """


class IInfo(interface.Interface):
    """ JSON Info Interface
    """

    def to_dict():
        """ return the dictionary representation of the object
        """

    def __call__():
        """ return the dictionary representation of the object
        """

# vim: set ft=python ts=4 sw=4 expandtab :
