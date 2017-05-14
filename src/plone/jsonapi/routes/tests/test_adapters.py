# -*- coding: utf-8 -*-

import os

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.jsonapi.routes.tests.base import APITestCase
from plone.jsonapi.routes import api
from plone.jsonapi.routes.interfaces import IInfo


FILENAME = u"TestDoc.docx"


def dummy_file():
    from plone.namedfile.file import NamedBlobImage
    path = os.path.join(os.path.dirname(__file__), FILENAME)
    return NamedBlobImage(
        data=open(path, 'r').read(),
        filename=FILENAME
    )


class TestDataproviders(APITestCase):
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
                                      title=FILENAME,
                                      file=file_contents)
        self.doc = self.portal.get(_)

        # handle plone 5 dexterity based file content
        if api.is_dexterity_content(self.doc):
            self.doc.file = dummy_file()
        else:
            self.doc.setFilename(FILENAME)

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
    #   Test Dataproviders
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
        self.assertEqual(data.get("uid"), '0')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDataproviders))
    return suite
