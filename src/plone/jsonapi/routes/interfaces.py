# -*- coding: utf-8 -*-

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.de>'
__docformat__ = 'plaintext'

from zope import interface


class IInfo(interface.Interface):
    """ JSON Info Interface
    """

    def __call__():
        """ return the dictionary representation of the object
        """

# vim: set ft=python ts=4 sw=4 expandtab :
