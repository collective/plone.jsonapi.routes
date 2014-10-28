# -*- coding: utf-8 -*-

import simplejson as json

import unittest2 as unittest

from plone.testing.z2 import Browser

from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig


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
        from plone.jsonapi.core import router
        from plone.jsonapi.routes import initialize

        self.app     = self.layer.get("app")
        self.portal  = self.layer.get("portal")
        self.request = self.layer.get("request")

        initialize(self.portal)
        router.DefaultRouter.initialize(self.portal, self.request)

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

# vim: set ft=python ts=4 sw=4 expandtab :
