# -*- coding: utf-8 -*-

import doctest
import simplejson as json

import unittest2 as unittest

from plone.testing.z2 import Browser

from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig

from Testing import ZopeTestCase as ztc


class TestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.jsonapi.core
        import plone.jsonapi.routes
        xmlconfig.file('configure.zcml', plone.jsonapi.core, context=configurationContext)
        xmlconfig.file('configure.zcml', plone.jsonapi.routes, context=configurationContext)

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser('admin',
                                           'secret',
                                           ['Manager'],
                                           [])
        login(portal, 'admin')
        # enable workflow for browser tests
        workflow = portal.portal_workflow
        workflow.setDefaultChain('simple_publication_workflow')

        # add a folder, so we can test with it
        portal.invokeFactory("Folder",
                             "folder",
                             title="Test Folder")

TEST_FIXTURE = TestLayer()
INTEGRATION_TESTING = IntegrationTesting(bases=(TEST_FIXTURE,),
                          name="plone.jsonapi.routes:Integration")


class APITestCase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        import plone.jsonapi.routes
        self.app     = self.layer.get("app")
        self.portal  = self.layer.get("portal")

    def getBrowser(self, handleErrors=False):
        browser = Browser(self.app)
        if handleErrors:
            browser.handleErrors = True
        return browser

    def decode(self, s):
        return json.loads(s)

    def create(self, what, where, id, **kw):
        login(self.portal, 'admin')
        where.invokeFactory(what, id, **kw)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        ztc.ZopeDocFileSuite(
            '../docs/Readme.txt',
            test_class=APITestCase,
            optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        ),
    ])
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
