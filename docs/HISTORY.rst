Changelog
=========

0.4 - unreleased
----------------

**FIXED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/22: Absoulte url is missing in update/create response
- https://github.com/collective/plone.jsonapi.routes/issues/21: Image Route throws an error

**ENHANCEMENTS**

- https://github.com/collective/plone.jsonapi.routes/issues/20: Support query for DateTime Indexes
- https://github.com/collective/plone.jsonapi.routes/issues/23: Support query for created/modified DateTime ranges

**OTHER CHANGES**

- added `/auth` route to enforce a basic auth
- added a custom exception class to set the right response status
- added `recent_modified` and `recent_created` handling
- added unittests for the `api` and `request` module
- no more request passing anymore - all handled by the request module now


0.3 - 2014-10-14
----------------

**FIXED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/16: Files can not be created/updated with base64 encoded data

- https://github.com/collective/plone.jsonapi.routes/issues/10: Fails on NamedBlobFile dexterity fields

- https://github.com/collective/plone.jsonapi.routes/pull/11: Typo in brain adapter

- https://github.com/collective/plone.jsonapi.routes/issues/14: Missing UIDs for complete objects

**ENHANCEMENTS**

- https://github.com/collective/plone.jsonapi.routes/issues/12: Add batching

- https://github.com/collective/plone.jsonapi.routes/issues/13: Add a flag to return the full fledged object results immediately

- https://github.com/collective/plone.jsonapi.routes/issues/19: Need to do a GET on a file using file path without using uid

- https://github.com/collective/plone.jsonapi.routes/issues/18: destination handling

- https://github.com/collective/plone.jsonapi.routes/issues/3: Add buildout configs inside package


**DOCUMENTATION**

- https://github.com/collective/plone.jsonapi.routes/issues/2: Sphinx documentation started


0.2 - 2014-03-05
----------------

**FIXED ISSUES**

- https://github.com/ramonski/plone.jsonapi.routes/issues/5: Dexterity support

- https://github.com/ramonski/plone.jsonapi.routes/issues/4: Update on UID Urls not working

- https://github.com/ramonski/plone.jsonapi.routes/issues/1: Started with some basic browsertests


**API CHANGES**

- API root url provided.

- Image and file fields are now rendered as a nested structure, e.g::

      {
        data: b64,
        size: 42,
        content_type: "image/png"
      }

- Workflow info is provided where possible, e.g::

      {
        status: "Private",
        review_state: "private",
        transitions: [
          {
            url: ".../content_status_modify?workflow_action=submit",
            display: "Puts your item in a review queue, so it can be published on the site.",
            value: "submit"
          },
        ],
        workflow: "simple_publication_workflow"
      }


0.1 - 2014-01-23
----------------

- first public release

.. vim: set ft=rst ts=4 sw=4 expandtab tw=78 :
