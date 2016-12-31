# -*- coding: utf-8 -*-

import json

from plone.jsonapi.routes.tests.base import APITestCase
from plone.jsonapi.routes import request as req


class TestRequest(APITestCase):
    """ Test the request API
    """

    def setUp(self):
        self.portal = self.getPortal()
        self.request = self.getRequest()

    def test_complete_parameter(self):
        self.assertFalse(req.get_complete())
        request = req.get_request()
        request.form["complete"] = "yes"
        self.assertTrue(req.get_complete())

    def test_sort_limit_parameter(self):
        self.assertEqual(req.get_sort_limit(), None)
        request = req.get_request()
        request.form["sort_limit"] = 1
        self.assertEqual(req.get_sort_limit(), 1)

    def test_batch_size_parameter(self):
        self.assertEqual(req.get_batch_size(), 25)
        request = req.get_request()
        request.form["limit"] = 1
        self.assertEqual(req.get_batch_size(), 1)

    def test_batch_start_parameter(self):
        self.assertEqual(req.get_batch_start(), 0)
        request = req.get_request()
        request.form["b_start"] = 1
        self.assertEqual(req.get_batch_start(), 1)

    def test_sort_on_parameter(self):
        self.assertEqual(req.get_sort_on(), "getObjPositionInParent")
        request = req.get_request()
        request.form["sort_on"] = "Title"
        self.assertEqual(req.get_sort_on(), "Title")

    def test_sort_order_parameter(self):
        self.assertEqual(req.get_sort_order(), "ascending")
        request = req.get_request()
        request.form["sort_order"] = "desc"
        self.assertEqual(req.get_sort_order(), "descending")
        request.form["sort_order"] = "DESC"
        self.assertEqual(req.get_sort_order(), "descending")

    def test_query_parameter(self):
        self.assertEqual(req.get_query(), "")
        request = req.get_request()
        request.form["q"] = "#*!$Foo"
        self.assertEqual(req.get_query(), "Foo*")

    def test_path_parameter(self):
        self.assertEqual(req.get_path(), "")
        request = req.get_request()
        request.form["path"] = "/Plone/folder"
        self.assertEqual(req.get_path(), "/Plone/folder")

    def test_depth_parameter(self):
        self.assertEqual(req.get_depth(), 0)
        request = req.get_request()
        request.form["depth"] = 5
        self.assertEqual(req.get_depth(), 5)

    def test_recent_modified_parameter(self):
        self.assertEqual(req.get_recent_modified(), None)
        request = req.get_request()
        request.form["recent_modified"] = "this-week"
        self.assertEqual(req.get_recent_modified(), "this-week")

    def test_recent_created_parameter(self):
        self.assertEqual(req.get_recent_created(), None)
        request = req.get_request()
        request.form["recent_created"] = "this-week"
        self.assertEqual(req.get_recent_created(), "this-week")

    def test_request_data(self):
        self.assertEqual(req.get_request_data(), [{}])
        data = {"title": "test"}
        self.request["BODY"] = json.dumps(data)
        self.assertEqual(req.get_request_data(), [data])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRequest))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
