# -*- coding: utf-8 -*-

import os
import json

import transaction
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

from plone.jsonapi.routes import adapters
from plone.jsonapi.routes.tests.base import APITestCase

API_BASE_URL = "/@@API/plone/api/1.0"
FILENAME = u"TestDoc.docx"


def dummy_file():
    from plone.namedfile.file import NamedBlobFile
    path = os.path.join(os.path.dirname(__file__), FILENAME)
    return NamedBlobFile(
        data=open(path, 'r').read(),
        filename=FILENAME
    )


class TestFilesAPI(APITestCase):
    """ Test the Files API
    """

    def setUp(self):
        self.app = self.getApp()
        self.portal = self.getPortal()
        self.request = self.getRequest()
        self.portal_url = self.portal.absolute_url()
        self.api_url = self.portal_url + API_BASE_URL

        # give the test user the manager role
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def get_response(self):
        """ Return the JSON decoded contents of the test browser
        """
        return json.loads(self.browser.contents)

    def get_key(self, key, default=None):
        """ return the key from the response JSON
        """
        response = self.get_response()
        return response.get(key, default)

    def get_items(self):
        """ return the items from the response JSON
        """
        response = self.get_response()
        return response.get("items")

    def test_files_route(self):
        """ Test CRUD file routes
        """
        # Call the files route
        self.browser.open(self.api_url + "/files")
        # There should be no file in the portal
        self.assertEqual(self.get_key("count"), 0)

        # Add a Word Document
        path = os.path.join(os.path.dirname(__file__), FILENAME)
        file_contents = open(path).read()
        _ = self.portal.invokeFactory("File",
                                      FILENAME,
                                      title=FILENAME,
                                      file=file_contents)

        transaction.commit()
        obj = self.portal.get(_)

        # handle plone 5 dexterity based file content
        if adapters.is_dexterity_content(obj):
            obj.file = dummy_file()
            transaction.commit()

        self.browser.open(self.api_url + "/files")
        # There should be one file in the portal
        self.assertEqual(self.get_key("count"), 1)

        # Get the Item
        item = self.get_items().pop()
        # Test if it is has the same ID
        self.assertEqual(item.get("id"), FILENAME)
        # Test if it is has the same UID
        self.assertEqual(item.get("uid"), obj.UID())

        # Issue #57: Explicitly ask for the filedata
        self.browser.open(self.api_url + "/files/%s?filedata=yes&complete=yes" % obj.UID())

        # Get the items list from the detail page
        items = self.get_items()
        # There should be exactly one item in the list

        self.assertEqual(len(items), 1)

        # Check the file contents
        file_data = items[0]["file"]

        # File contents should be the same (base64 encoded)
        self.assertEqual(
            file_data.get("data"),
            str(file_contents).encode("base64")
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFilesAPI))
    return suite
