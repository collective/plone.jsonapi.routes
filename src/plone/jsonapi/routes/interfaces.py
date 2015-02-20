# -*- coding: utf-8 -*-

from zope import interface

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.de>'
__docformat__ = 'plaintext'


class IInfo(interface.Interface):
    """ JSON Info Interface
    """

    def to_dict():
        """ return the dictionary representation of the object
        """

    def __call__():
        """ return the dictionary representation of the object
        """


class IBatch(interface.Interface):
    """ Batch Interface
    """

    def get_batch():
        """ return the wrapped batch object
        """

    def get_pagesize():
        """ return the current page size
        """

    def get_pagenumber():
        """ return the current page number
        """

    def get_numpages():
        """ return the current number of pages
        """

    def get_sequence_length():
        """ return the length
        """

    def make_next_url():
        """ build and return the next url
        """

    def make_prev_url():
        """ build and return the previous url
        """


class IDataManager(interface.Interface):
    """ Field Interface
    """

    def get(name):
        """ Get the value of the named field with
        """

    def set(name, value):
        """ Set the value of the named field
        """
