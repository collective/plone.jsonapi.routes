# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from plone.jsonapi.routes.tests.base import APITestCase


class TestSetup(APITestCase):
    """ Test URL registration machinery
    """

    def testCRUDEndpoint(self):
        endpoint = "get"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testCollectionsEndpoint(self):
        endpoint = "collections"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testDocumentsEndpoint(self):
        endpoint = "documents"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testEventsEndpoint(self):
        endpoint = "events"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testFilesEndpoint(self):
        endpoint = "files"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testFoldersEndpoint(self):
        endpoint = "folders"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testImagesEndpoint(self):
        endpoint = "images"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testLinksEndpoint(self):
        endpoint = "links"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testNewsItemsEndpoint(self):
        endpoint = "newsitems"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testSearchEndpoint(self):
        endpoint = "search"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testTopicEndpoint(self):
        endpoint = "topics"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)

    def testUsersEndpoint(self):
        endpoint = "users"
        self.assertEqual(router.url_for(endpoint),
                         "/plone/@@API/plone/api/1.0/%s" % endpoint)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetup))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
