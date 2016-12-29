# -*- coding: utf-8 -*-

import pkg_resources

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


def version():
    dist = pkg_resources.get_distribution("plone.jsonapi.routes")
    return dist.version

__version__ = version()
__build__ = 510
__date__ = '2016-12-28'
