# -*- coding: utf-8 -*-

import doctest

import unittest2 as unittest

import plone.jsonapi.routes.underscore


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        doctest.DocTestSuite(
            module=plone.jsonapi.routes.underscore,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
        ),
    ])
    return suite
