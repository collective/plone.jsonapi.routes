# -*- coding: utf-8 -*-

import os

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.jsonapi.routes.tests.base import APITestCase
from plone.jsonapi.routes import api
from plone.jsonapi.routes import adapters
from plone.jsonapi.routes.interfaces import IInfo


class TestAdapters(APITestCase):
    """ Test the Data Adapter
    """

    def setUp(self):
        self.portal = self.getPortal()
        self.request = self.getRequest()

        # the test folder we created
        self.test_folder = self.portal.folder

        # give the test user the manager role
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # Add a Word Document
        path = os.path.join(os.path.dirname(__file__), u'TestDoc.docx')
        file_contents = open(path).read()
        _ = self.portal.invokeFactory("File",
                                      "testdoc.docx",
                                      title="TestDoc.docx",
                                      file=file_contents)
        self.doc = self.portal.get(_)

    # -----------------------------------------------------------------------------
    #   Testing Helpers
    # -----------------------------------------------------------------------------

    def get_document_obj(self):
        _, obj = self.test_folder.items()[0]
        return obj

    def get_document_brain(self):
        pc = api.get_portal_catalog()
        results = pc({"portal_type": "Document", "limit": 1})
        return results[0]

    # -----------------------------------------------------------------------------
    #   Test Adapters
    # -----------------------------------------------------------------------------

    def test_brain_adapter(self):
        brain = self.get_document_brain()
        adapter = IInfo(brain)
        data = adapter()
        self.assertEqual(data.get("uid"), brain.UID)

    def test_at_adapter(self):
        obj = self.get_document_obj()
        adapter = IInfo(obj)
        data = adapter()
        self.assertEqual(data.get("uid"), obj.UID())

    def test_portal_adapter(self):
        obj = self.portal
        adapter = IInfo(obj)
        data = adapter()
        self.assertEqual(data.get("uid"), 0)

    # -----------------------------------------------------------------------------
    #   Test Functional Helpers
    # -----------------------------------------------------------------------------

    def test_extract_fields(self):
        # extract fields from content objects
        obj = self.get_document_obj()
        data = adapters.extract_fields(obj, ["title"])
        self.assertEqual(data.get("title"), obj.title)
        # extract fields from catalog brains
        brain = self.get_document_brain()
        data = adapters.extract_fields(brain, ["UID"])
        self.assertEqual(data.get("UID"), brain.UID)

    def test_get_json_value(self):
        # Ensure JSON serializable handling of a Schema field value
        obj = self.get_document_obj()

        # handles date objects
        value = adapters.get_json_value(obj, "creation_date")
        self.assertEqual(value, obj.created().ISO8601())

        # extracts the value by name if omitted
        value = adapters.get_json_value(obj, "title")
        self.assertEqual(value, obj.Title())

        # takes the given value
        value = adapters.get_json_value(obj, "foo", 1)
        self.assertEqual(type(value), int)

        # returns the default if the value is not JSON serializable
        value = adapters.get_json_value(obj, "object", object(),
                                        default="Not JSON serializable")
        self.assertEqual(value, "Not JSON serializable")

    def test_get_file_info(self):
        obj = self.doc
        # extract the file info
        info = adapters.get_file_info(obj, "file")
        self.assertEqual(info.get("filename"), obj.getFilename())

    def test_get_download_url(self):
        obj = self.doc
        # extract the file info
        info = adapters.get_download_url(obj, "file")
        self.assertTrue(info.endswith("%s/download" % obj.getId()))

    def test_get_content_type(self):
        obj = self.doc
        # extracts the content type of content objects
        ct = adapters.get_content_type(obj)
        self.assertEqual(ct, obj.getContentType())
        # it also handles blob wrappers
        ct = adapters.get_content_type(obj.getBlobWrapper())
        self.assertEqual(ct, obj.getContentType())
        # it handles non known objects gracefully
        ct = adapters.get_content_type(object(), "binary")
        self.assertEqual(ct, "binary")

    def test_get_iso_date(self):
        obj = self.get_document_obj()
        created = obj.created()
        date = adapters.get_iso_date(created)
        self.assertEqual(date, obj.created().ISO8601())

    def test_is_dexterity_content(self):
        obj = self.get_document_obj()
        self.assertFalse(adapters.is_dexterity_content(obj))

    def test_is_file_field(self):
        obj = self.doc
        field = obj.getField("title")
        self.assertFalse(adapters.is_file_field(field))
        field = obj.getBlobWrapper()
        self.assertTrue(adapters.is_file_field(field))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAdapters))
    return suite
