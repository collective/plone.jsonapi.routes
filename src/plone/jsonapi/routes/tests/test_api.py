# -*- coding: utf-8 -*-

import json

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.jsonapi.routes.tests.base import APITestCase
from plone.jsonapi.routes import api

from Products.CMFCore.utils import getToolByName


class TestAPI(APITestCase):
    """ Test the API functionality
    """

    def setUp(self):
        self.portal = self.getPortal()
        self.request = self.getRequest()

        # the test folder we created
        self.test_folder = self.portal.folder

        # give the test user the manager role
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

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
    #   Test Data Functions
    # -----------------------------------------------------------------------------

    def test_get_search_results(self):
        # query portal
        result = api.get_search_results(portal_type="Plone Site")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.portal)
        result = api.get_search_results(uid="0")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], self.portal)
        # query contents
        result = api.get_search_results(portal_type="Document")
        self.assertEqual(len(result), 50)

    def test_get_search_results_issue75(self):
        # handle api invocation gracefully if w/o Plone site
        def faux_get_portal():
            return []
        get_portal = api.get_portal
        api.get_portal = faux_get_portal
        result = api.get_search_results(portal_type="Plone Site")
        self.assertEqual(len(result), 0)
        api.get_portal = get_portal

    def test_make_items_for(self):
        # handles empty data gracefully
        self.assertEqual(api.make_items_for([]), [])
        # returns brain results
        brain = self.get_document_brain()
        self.assertEqual(len(api.make_items_for([brain])), 1)
        self.assertEqual(
            api.make_items_for([brain])[0]["id"],
            brain.getId)
        # returns object results
        obj = self.get_document_obj()
        self.assertEqual(len(api.make_items_for([obj])), 1)
        self.assertEqual(
            api.make_items_for([obj])[0]["uid"],
            obj.UID())

    def test_get_info(self):
        # returns brain data
        brain = self.get_document_brain()
        self.assertEqual(
            api.get_info(brain).get("id"),
            brain.getId)
        # returns object results
        obj = self.get_document_obj()
        self.assertEqual(
            api.get_info(obj).get("uid"),
            obj.UID())

    def test_get_url_info(self):
        # returns brain data
        brain = self.get_document_brain()
        self.assertEqual(
            api.get_url_info(brain).get("url"),
            brain.getURL())
        # returns object data
        obj = self.get_document_obj()
        self.assertEqual(
            api.get_url_info(obj).get("url"),
            obj.absolute_url())

    def test_get_workflow_info(self):
        # returns brain data
        brain = self.get_document_brain()
        # XXX test with assigned worklfow
        self.assertEqual(api.get_workflow_info(brain), {})
        # returns object data
        obj = self.get_document_obj()
        # XXX test with assigned worklfow
        self.assertEqual(api.get_workflow_info(obj), {})

    def test_get_parent_info(self):
        # handles the portal object gracefully
        self.assertEqual(api.get_parent_info(self.portal), {})
        # handles catalog brains
        brain = self.get_document_brain()
        self.assertEqual(
            api.get_parent_info(brain).get("parent_id"),
            self.portal.folder.getId())
        # handles content objects
        obj = self.get_document_obj()
        self.assertEqual(
            api.get_parent_info(obj).get("parent_id"),
            self.portal.folder.getId())

    def test_get_children_info(self):
        folder = self.portal.folder
        info = api.get_children_info(folder)
        children = info.get("children", [])
        # should contain 50 documents
        self.assertEqual(len(children), 50)

    def test_get_sharing_info(self):
        # returns brain data
        brain = self.get_document_brain()
        sharing = api.get_sharing_info(brain)
        # default sharing, inherit: true
        self.assertTrue(sharing['inherit'])
        # default sharing, one role setting for authenticated users
        self.assertEqual(
            sharing['role_settings'][0]['id'],
            'AuthenticatedUsers')

    # -----------------------------------------------------------------------------
    #   Test Functional Helpers
    # -----------------------------------------------------------------------------

    def test_get_portal(self):
        self.assertEqual(api.get_portal(), self.portal)

    def test_get_tool(self):
        self.assertEqual(
            api.get_tool("portal_catalog"),
            getToolByName(self.portal, "portal_catalog"))

    def test_get_portal_catalog(self):
        self.assertEqual(
            api.get_portal_catalog(),
            getToolByName(self.portal, "portal_catalog"))

    def test_get_portal_reference_catalog(self):
        try:
            rc = getToolByName(self.portal, "reference_catalog")
        except AttributeError:
            rc = None

        self.assertEqual(
            api.get_portal_reference_catalog(),
            rc)

    def test_get_portal_workflow(self):
        self.assertEqual(
            api.get_portal_workflow(),
            getToolByName(self.portal, "portal_workflow"))

    def test_is_brain(self):
        brain = self.get_document_brain()
        self.assertTrue(api.is_brain(brain))
        self.assertFalse(api.is_brain(api.get_object(brain)))

    def test_is_root(self):
        self.assertTrue(api.is_root(self.portal))

    def test_is_folderish(self):
        self.assertTrue(api.is_folderish(self.portal.folder))
        self.assertTrue(api.is_folderish(self.portal))
        self.assertFalse(api.is_folderish(self.get_document_brain()))

    def test_url_for(self):
        endpoint = "plone.jsonapi.routes.plonesites"
        uid = "0"
        self.assertEqual(
            api.url_for(endpoint, uid=uid),
            "http://foo/plone/api/1.0/plonesites/0")

    def test_get_url(self):
        self.assertEqual(
            api.get_url(self.portal),
            self.portal.absolute_url())

    def test_get_id(self):
        obj = self.get_document_obj()
        self.assertEqual(api.get_id(obj), obj.getId())

    def test_get_uid(self):
        obj = self.get_document_obj()
        self.assertEqual(api.get_uid(obj), obj.UID())

    def test_get_portal_type(self):
        self.assertEqual(
            api.get_portal_type(self.get_document_brain()),
            "Document")
        self.assertEqual(
            api.get_portal_type(self.get_document_obj()),
            "Document")

    def test_get_object(self):
        obj = self.get_document_obj()
        brain = self.get_document_brain()
        self.assertEqual(api.get_object(obj), obj)
        self.assertEqual(api.get_object(brain), brain.getObject())

    def test_get_parent(self):
        folder = self.test_folder
        # works for catalog brains
        brain = self.get_document_brain()
        parent = api.get_parent(brain)
        self.assertEqual(parent.UID, folder.UID())

        # works for content objects
        obj = self.get_document_obj()
        parent = api.get_parent(obj)
        self.assertEqual(parent, folder)

    def test_get_parent_path(self):
        folder = self.portal.folder
        parent_path = "/".join(folder.getPhysicalPath())

        # works for catalog objects
        brain = self.get_document_brain()
        self.assertEqual(api.get_parent_path(brain), parent_path)

        # works for content objects
        obj = self.get_document_obj()
        self.assertEqual(api.get_parent_path(obj), parent_path)

    def test_get_path(self):
        brain = self.get_document_brain()
        self.assertEqual(
            api.get_path(brain),
            brain.getPath())

    def test_get_contents(self):
        obj = self.portal.folder
        contents = api.get_contents(obj)

        # see base.py - we have 50 documents in there
        self.assertEqual(len(contents), 50)

        # we return always brains
        self.assertTrue(api.is_brain(contents[0]))

    def test_get_endpoint(self):
        obj = self.portal.folder
        # we should get the namespaced endpoint now by this function
        self.assertEqual(api.get_endpoint(obj), "plone.jsonapi.routes.folders")

    def test_find_objects(self):
        obj = self.portal.folder
        uid = obj.UID()
        self.assertEqual(api.find_objects(uid=uid), [obj])

    def test_get_object_by_request(self):
        obj = self.portal.folder
        request = self.getRequest()

        request.form["uid"] = obj.UID()
        self.assertEqual(api.get_object_by_request(), obj)

        del request.form["uid"]
        request.form["path"] = "/".join(obj.getPhysicalPath())
        self.assertEqual(api.get_object_by_request(), obj)

    def test_get_object_by_record(self):
        obj = self.portal.folder

        record = {"uid": obj.UID()}
        self.assertEqual(api.get_object_by_record(record), obj)

        record = {"path": "/".join(obj.getPhysicalPath())}
        self.assertEqual(api.get_object_by_record(record), obj)

    def test_get_object_by_uid(self):
        obj = self.get_document_obj()
        uid = obj.UID()
        self.assertEqual(api.get_object_by_uid(uid), obj)
        # specail case: UID 0 is the portal
        self.assertEqual(api.get_object_by_uid(0), self.portal)

    def test_get_object_by_path(self):
        obj = self.get_document_obj()
        path = "/".join(obj.getPhysicalPath())
        self.assertEqual(api.get_object_by_path(path), obj)

    def test_mkdir(self):
        obj = self.portal.folder
        path = "/".join(obj.getPhysicalPath())
        api.mkdir(path + "/subfolder"),
        subfolder = obj.get("subfolder")
        new_path = "/".join(subfolder.getPhysicalPath())
        self.assertEqual(path + "/subfolder", new_path)

    def test_find_target_container(self):
        obj = self.portal.folder
        record = {"parent_uid": obj.UID()}
        self.assertEqual(api.find_target_container(record), obj)

    def test_do_action_for(self):
        # XXX: TBD
        pass

    def test_delete_object(self):
        count = len(self.portal.folder.objectIds())
        brain = self.get_document_brain()
        api.delete_object(brain)
        self.assertEqual(
            len(self.portal.folder.objectIds()),
            count - 1)

    def test_get_current_user(self):
        user = api.get_current_user()
        self.assertEqual(user.id, TEST_USER_ID)

    def test_create_object(self):
        folder = self.portal.folder
        doc = api.create_object(folder, "Document")
        self.assertEqual(doc.UID(), folder.get(doc.id).UID())

    def test_update_object_with_data(self):
        doc = self.get_document_obj()
        api.update_object_with_data(doc, {"title": u"Changed"})
        title = getattr(doc, "title", None)
        self.assertEqual(title, u"Changed")


class TestCRUDAPI(APITestCase):
    """ Test the CREATE/UPDATE/DELETE functionality of the API
    """

    def setUp(self):
        self.portal = self.getPortal()
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
        data = {"id": "subfolder", "title": "Subfolder"}
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
