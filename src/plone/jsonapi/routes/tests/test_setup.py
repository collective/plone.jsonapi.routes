# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from plone.jsonapi.routes.tests.base import APITestCase

NAMESPACE = "plone.jsonapi.routes"


class TestSetup(APITestCase):
    """Test URL registration machinery
    """

    def testSearchEndpoint(self):
        endpoint = "search"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testUsersEndpoint(self):
        endpoint = "users"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite
