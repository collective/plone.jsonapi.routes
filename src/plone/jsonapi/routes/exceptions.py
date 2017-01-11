# -*- coding: utf-8 -*-

from plone.jsonapi.routes import request as req

__author__ = 'Ramon Bartl <rb@ridingbytes.com>'
__docformat__ = 'plaintext'


class APIError(Exception):
    """ Exception Class for API Errors
    """

    def __init__(self, status, message):
        self.message = message
        self.status = status
        self.setStatus(status)

    def setStatus(self, status):
        request = req.getRequest()
        request.response.setStatus(status)

    def __str__(self):
        return self.message
