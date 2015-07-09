# -*- coding: utf-8 -*-

import urllib
import logging

from zope import interface

from plone.jsonapi.routes.interfaces import IBatch

from plone.jsonapi.routes import request as req

__author__    = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


logger = logging.getLogger("plone.jsonapi.routes.batching")


class Batch(object):
    """ Adapter for Plone 4.3 batching functionality
    """
    interface.implements(IBatch)

    def __init__(self, batch):
        self.batch = batch

    def get_batch(self):
        return self.batch

    def get_pagesize(self):
        return self.batch.pagesize

    def get_pagenumber(self):
        return self.batch.pagenumber

    def get_numpages(self):
        return self.batch.numpages

    def get_sequence_length(self):
        return self.batch.sequence_length

    def make_next_url(self):
        if not self.batch.has_next:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = self.batch.pagenumber * self.batch.pagesize
        return "%s?%s" % (request.URL, urllib.urlencode(params))

    def make_prev_url(self):
        if not self.batch.has_previous:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = max(self.batch.pagenumber - 2, 0) * self.batch.pagesize
        return "%s?%s" % (request.URL, urllib.urlencode(params))


class Batch42(object):
    """ Adapter for Plone 4.2 batching functionality
    """
    interface.implements(IBatch)

    def __init__(self, batch):
        self.batch = batch

    def get_batch(self):
        return self.batch

    def get_pagesize(self):
        return self.batch.size

    def get_pagenumber(self):
        return self.batch.pagenumber

    def get_numpages(self):
        return self.batch.numpages

    def get_sequence_length(self):
        return self.batch.sequence_length

    def make_next_url(self):
        if self.batch.next is not None:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = self.batch.numpages * self.batch.size
        return "%s?%s" % (request.URL, urllib.urlencode(params))

    def make_prev_url(self):
        if self.batch.previous is not None:
            return None
        request = req.get_request()
        params = request.form
        params["b_start"] = max(self.batch.numpages - 2, 0) * self.batch.size
        return "%s?%s" % (request.URL, urllib.urlencode(params))
