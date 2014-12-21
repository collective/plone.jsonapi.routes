# -*- coding: utf-8 -*-

import json

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.jsonapi.routes.tests.base import APITestCase
from plone.jsonapi.routes import api



class TestAPI(APITestCase):
    """ Test the API functionality
    """

    def setUp(self):
        self.portal  = self.getPortal()
        self.request = self.getRequest()

        # the test folder we created
        self.test_folder = self.portal.folder

        # give the test user the manager role
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def get_document_obj(self):
        _, obj = self.test_folder.items()[0]
        return obj

    def get_document_brain(self):
        pc = api.get_portal_catalog()
        results = pc({"portal_type": "Document", "limit":1})
        return results[0]

    def test_get_portal(self):
        self.assertEqual(api.get_portal(), self.portal)

    def test_is_brain(self):
        brain = self.get_document_brain()
        self.assertTrue(api.is_brain(brain))
        self.assertFalse(api.is_brain(api.get_object(brain)))

    def test_get_uid(self):
        obj = self.get_document_obj()
        self.assertEqual(api.get_uid(obj), obj.UID())

    def test_get_parent(self):
        parent = self.test_folder
        obj = self.get_document_obj()
        self.assertEqual(api.get_parent(obj), parent)

    def test_get_object(self):
        obj = self.get_document_obj()
        brain = self.get_document_brain()
        self.assertEqual(api.get_object(obj), obj)
        self.assertEqual(api.get_object(brain), brain.getObject())

    def test_get_object_by_uid(self):
        obj = self.get_document_obj()
        uid = obj.UID()
        self.assertEqual(api.get_object_by_uid(uid), obj)
        # specail case: UID 0 is the portal
        self.assertEqual(api.get_object_by_uid(0), self.portal)


class TestCRUDAPI(APITestCase):
    """ Test the CREATE/UPDATE/DELETE functionality of the API
    """

    def setUp(self):
        self.portal  = self.getPortal()
        self.request = self.getRequest()

        # the test folder we created
        self.test_folder = self.portal.folder

        # give the test user the manager role
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_get_items(self):
        results = api.get_items("Folder")
        self.assertEqual(len(results), 1)

    def test_get_batched(self):
        results = api.get_batched("Document")
        self.assertEqual(results["count"], 50)
        self.assertEqual(results["pages"], 2)

    def test_create_items(self):
        # create a folder inside the testfolder
        data = {"title": "Subfolder"}
        self.request["BODY"] = json.dumps(data)
        api.create_items("Folder", uid=self.test_folder.UID())
        results = api.get_items("Folder")
        self.assertEqual(len(results), 2)
        self.assertEqual(self.test_folder.subfolder.Title(), "Subfolder")

    def test_update_items(self):
        data = {"title": "Test Folder Changed"}
        self.request["BODY"] = json.dumps(data)
        self.assertEqual(self.test_folder.Title(), "Test Folder")
        api.update_items("Folder", uid=self.test_folder.UID())
        self.assertEqual(self.test_folder.Title(), data["title"])

    def test_delete_items(self):
        api.delete_items("Folder", uid=self.test_folder.UID())
        self.assertEqual(len(api.get_items("Folder")), 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAPI))
    suite.addTest(makeSuite(TestCRUDAPI))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
