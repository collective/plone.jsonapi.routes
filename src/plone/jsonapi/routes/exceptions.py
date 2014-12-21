# -*- coding: utf-8 -*-

__author__    = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


from plone.jsonapi.routes import request as req


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

# vim: set ft=python ts=4 sw=4 expandtab :
