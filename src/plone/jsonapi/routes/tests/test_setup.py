# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from plone.jsonapi.routes.tests.base import APITestCase

NAMESPACE = "plone.jsonapi.routes"


class TestSetup(APITestCase):
    """ Test URL registration machinery
    """

    def testCRUDEndpoint(self):
        endpoint = "get"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testCollectionsEndpoint(self):
        endpoint = "collections"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testDocumentsEndpoint(self):
        endpoint = "documents"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testEventsEndpoint(self):
        endpoint = "events"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testFilesEndpoint(self):
        endpoint = "files"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testFoldersEndpoint(self):
        endpoint = "folders"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testImagesEndpoint(self):
        endpoint = "images"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testLinksEndpoint(self):
        endpoint = "links"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testNewsItemsEndpoint(self):
        endpoint = "newsitems"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testSearchEndpoint(self):
        endpoint = "search"
        namespace_endpoint = ".".join([NAMESPACE, endpoint])
        self.assertEqual(router.url_for(namespace_endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testTopicEndpoint(self):
        endpoint = "topics"
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
