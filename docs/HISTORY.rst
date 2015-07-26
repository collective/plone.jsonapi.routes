.. _Changelog:

Changelog
=========

0.9 - unreleased
----------------

- https://github.com/collective/plone.jsonapi.routes/issues/47: ZCML directive to enable AdvancedQuery if installed


0.8 - 2015-07-20
----------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/45: Add authentication routes
- https://github.com/collective/plone.jsonapi.routes/issues/44: Add the filename to the JSON data
- https://github.com/collective/plone.jsonapi.routes/issues/43: API: Intermediate Folder creation
- https://github.com/collective/plone.jsonapi.routes/issues/41: Field Type Validation
- https://github.com/collective/plone.jsonapi.routes/issues/42: ContentType for Dexterity Files CT


0.7 - 2015-07-09
----------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/9:  Handle Dexterity Behavior fields
- https://github.com/collective/plone.jsonapi.routes/issues/38: Filename handling
- https://github.com/collective/plone.jsonapi.routes/issues/36: Mime Type handling


**OTHER CHANGES**

- Updated Documentation
- Request module: Added helper functions
- Travis CI integration


0.6 - 2015-02-22
----------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/33: Image detail URL throws error
- https://github.com/collective/plone.jsonapi.routes/issues/34: Failed POST request return HTTP 200
- https://github.com/collective/plone.jsonapi.routes/issues/35: DataManager does not check field permissions


0.5 - 2015-02-20
----------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/32: Add documentation for the new ZPublisher record behavior
- https://github.com/collective/plone.jsonapi.routes/issues/31: Change default sort order to ascending
- https://github.com/collective/plone.jsonapi.routes/pull/30:   fix standard query ignoring sort_on and sort_order
- https://github.com/collective/plone.jsonapi.routes/issues/27: querying does not support ZPublisher record format
- https://github.com/collective/plone.jsonapi.routes/issues/25: Add support for Plone 4.2

**OTHER CHANGES**

- Added batch adapter
- Added more tests


0.4 - 2015-01-13
----------------

**FIXED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/22: Absoulte url is missing in update/create response
- https://github.com/collective/plone.jsonapi.routes/issues/21: Image Route throws an error

**ENHANCEMENTS**

- https://github.com/collective/plone.jsonapi.routes/issues/20: Support query for DateTime Indexes
- https://github.com/collective/plone.jsonapi.routes/issues/23: Support query for created/modified DateTime ranges

**OTHER CHANGES**

- added `IDataManager` field data manager
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
