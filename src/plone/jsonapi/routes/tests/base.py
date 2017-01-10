# -*- coding: utf-8 -*-

import simplejson as json

from zope.configuration import xmlconfig

import unittest2 as unittest

from plone import api

from plone.testing import z2
from plone.testing.z2 import Browser

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import IntegrationTesting

from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE


class TestLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.jsonapi.core
        import plone.jsonapi.routes
        xmlconfig.file('configure.zcml', plone.jsonapi.core,
                       context=configurationContext)
        xmlconfig.file('configure.zcml', plone.jsonapi.routes,
                       context=configurationContext)

        # Install product and call its initialize() function
        z2.installProduct(app, 'plone.jsonapi.core')
        z2.installProduct(app, 'plone.jsonapi.routes')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'plone.jsonapi.core')
        z2.uninstallProduct(app, 'plone.jsonapi.routes')

    def setUpPloneSite(self, portal):
        setRoles(portal, TEST_USER_ID, ['Manager'])

        # fix for *** ValueError: No such content type: Folder
        if api.env.plone_version().startswith("5"):
            portal.portal_quickinstaller.installProduct("plone.app.contenttypes")

        # add a folder, so we can test with it
        _ = portal.invokeFactory("Folder", "folder", title="Test Folder")
        folder = portal[_]
        for i in range(50):
            folder.invokeFactory("Document", "document-%d" % i,
                                 title="Test Document %d" % i)

        # Test fixture -- p.j.c. needs to have a request
        from plone.jsonapi.core import router
        router.DefaultRouter.initialize(portal, portal.REQUEST)

        # add a custom metadata column to portal_catalog so
        # we can test it gets included in json output
        portal.portal_catalog.addColumn('title_or_id')
        portal.portal_catalog.refreshCatalog(clear=0)


TEST_FIXTURE = TestLayer()

INTEGRATION_TESTING = IntegrationTesting(
    bases=(TEST_FIXTURE,),
    name="plone.jsonapi.routes:Integration")

ROBOT_TESTING = FunctionalTesting(
    bases=(TEST_FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="plone.jsonapi.routes:Robot")


class APITestCase(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def getBrowser(self, handleErrors=False):
        browser = Browser(self.getApp())
        if handleErrors:
            browser.handleErrors = True
        return browser

    def getApp(self):
        return self.layer.get("app")

    def getPortal(self):
        return self.layer.get("portal")

    def getRequest(self):
        return self.layer.get("request")

    def decode(self, s):
        return json.loads(s)
