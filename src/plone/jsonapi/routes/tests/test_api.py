# -*- coding: utf-8 -*-

import json

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.jsonapi.routes.tests.base import APITestCase
from plone.jsonapi.routes import api


class TestAPI(APITestCase):

    def test_get_items(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        results = api.get_items("Folder")
        self.assertEqual(len(results), 1)

    def test_get_batched(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        results = api.get_batched("Document")
        self.assertEqual(results["count"], 50)
        self.assertEqual(results["pages"], 2)

    def test_create_items(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # create a folder inside the testfolder
        data = {"title": "Subfolder"}
        self.request["BODY"] = json.dumps(data)
        api.create_items("Folder", uid=self.test_folder.UID())
        results = api.get_items("Folder")
        self.assertEqual(len(results), 2)
        self.assertEqual(self.test_folder.subfolder.Title(), "Subfolder")

    def test_update_items(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        data = {"title": "Test Folder Changed"}
        self.request["BODY"] = json.dumps(data)
        self.assertEqual(self.test_folder.Title(), "Test Folder")
        api.update_items("Folder", uid=self.test_folder.UID())
        self.assertEqual(self.test_folder.Title(), data["title"])

    def test_delete_items(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.delete_items("Folder", uid=self.test_folder.UID())
        self.assertEqual(len(api.get_items("Folder")), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAPI))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
