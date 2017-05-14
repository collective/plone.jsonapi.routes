Changelog
=========


0.9.3 - 2017-05-14
------------------

**Changes**

- `IDataManager` contain now a `json_data` method to return a JSON suitable
  return structure or delegate to the `IFieldManager.json_data` method.
  Please see section "Customizing" in the documentation for more details.
- Added support for `z3c.relationfield.interfaces.IRelationList` fields
- Added support for `plone.app.textfield.interfaces.IRichText` fields
- Added support for `plone.app.blob.interfaces.IBlobField` fields
- More code cleanup and refactoring (coming closer to a robust 1.0.0 release!)


0.9.2 - 2017-05-12
------------------

**Changes**

- Added `IFieldManager` adapter to `get` and `set` the value on field level.
- Removed `build` number from version route JSON response.
- Content route improved.
- API refactored.
- Improved `users` route.
- Updated documentation


0.9.1 - 2017-04-20
------------------

**Changes**

- Added `ICatalog` and `ICatalogQuery` adapter for full search control. See docs for usage.
- Removed `query` module in favor of the new adapters.
- Removed multiple catalog query functionality. Please define a custom `ICatalog` adapter if you need it.
- Added generic route provider for all `portal_types`.
  N.B. The old-style route providers, e.g. `folders`, `documents` etc., are now obsolete.
  Please use the lower portal type name instead, e.g. `folder`, `docuememt` ...
- The `users` route shows now more details of the users and results are now batched.
- Removed default `getObjPositionInParent` sorting. Please specify explicitly via `sort_on`.
- UID of the plone site is now '0' instead of 0.
- Huge code refactoring and cleanup.


0.9.0 - 2017-01-12
------------------

**Changes**

- API mthods `get_items` and `get_batched` accept now keyword paramters.
  Keywords can be catalog indexes, e.g. `id=document-1` or a complete catalog
  query objejt, e.g. `query={'portal_type': 'Document'}`.
- Changed `get_contents` method to use the `search` functionality from the
  `query` module.
- More doctests added


0.8.9 - 2017-01-11
------------------

**Changes**

- Catalog to query can now be set via the `catalog` request parameter.
- Optimized search logic
- Fixed issue with multiple `portal_type` parameters in request
- Code Refactoring
- More tests


0.8.8 - 2017-01-10
------------------

**Changes**

- Handle catalog queries for multiple contents, which might be located in
  different catalogs.
- Fixed an issue where the batch navigation did not show more results when using
  multiple `portal_type` request parameters.


0.8.7 - 2017-01-10
------------------

**Changes**

- Handle Reference Fields: Reference fields containing a reference can be
  updated with a dictionary, e.g.::

      {
        uid: <UID of a content containing a reference field>,
        ReferenceField: {
          "title": "New Title"
        }
      }

- Added module `underscore` to the tests suite
- Validation for the entire object added
- Get the catalog to query from Archtype Tool and default to `portal_catalog`
- Use explicit namespace in route providers
- Handle Reference Fields (Fields containing and `ImplicitAcquisitionWrapper` object)
- Added ZCML directive to enable/disable route registrations (default enabled)::

    <!-- Disable route registration -->
    <plone:jsonapi
        register_api_routes="False"
    />

- Version route is now part of the standard route providers
- Dropped AdvancedQuery handling


0.8.6 - 2016-04-08
------------------

Fix for broken release 0.8.5


0.8.5 - 2016-04-08
------------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/59: API URL for non standard content types
- https://github.com/collective/plone.jsonapi.routes/issues/60: Add a namespace to the route registrations
- https://github.com/collective/plone.jsonapi.routes/issues/63: handle richtext fields
- https://github.com/collective/plone.jsonapi.routes/issues/82: Plone 5 CSFR Protection
- https://github.com/collective/plone.jsonapi.routes/issues/80: Tests for Plone 5
- https://github.com/collective/plone.jsonapi.routes/issues/77: Problem with creating files
- https://github.com/collective/plone.jsonapi.routes/issues/62: 'reference_catalog' not found
- https://github.com/collective/plone.jsonapi.routes/pull/75: Fix api invocation on the zope root
- https://github.com/collective/plone.jsonapi.routes/pull/74: Reuse and improve code to check if a parameter in the request has a True value
- https://github.com/collective/plone.jsonapi.routes/pull/73: Using specifiers to format string (helps compatibility with Python 2.6, improves code readability)


0.8.4 - 2016-01-14
------------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/pull/66: api routes: sharing (docs)
- https://github.com/collective/plone.jsonapi.routes/pull/65: api routes: sharing (code)
- https://github.com/collective/plone.jsonapi.routes/pull/61: Use IConstrainTypes adapters for dexterity content

**API CHANGES**

- Sharing information can be displayed for objects. Use `?sharing=yes`


0.8.3 - 2015-09-14
------------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/58: Unit tests: add tests for adapter module
- https://github.com/collective/plone.jsonapi.routes/issues/57: API Change: workflow data optional
- https://github.com/collective/plone.jsonapi.routes/issues/54: Let complete flag overrule "uid rule"
- https://github.com/collective/plone.jsonapi.routes/issues/53: Unit tests: add tests for api module

**API CHANGES**

- File data **not** included by default anymore. Use `?filedata=yes`

- Workflow data **not** included by default anymore. Use `?workflow=yes`

- Workflow data is now located at the key `workflow`

- The complete flag can be now negated, even if the full object is displayes `?complete=no`

- The `state` key is removed -- use `review_state` instead

- Parent URL data included now for brain results


0.8.2 - 2015-09-09
------------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/52: Handle field unauthorized errors in the GET API
- https://github.com/collective/plone.jsonapi.routes/issues/51: Default Data Adapters missing


0.8.1 - 2015-09-06
------------------

**CLOSED ISSUES**

- https://github.com/collective/plone.jsonapi.routes/issues/50: API route throws error
- https://github.com/collective/plone.jsonapi.routes/pull/37:   Include custom metadata columns
- https://github.com/collective/plone.jsonapi.routes/pull/37:   Include custom metadata columns
- https://github.com/collective/plone.jsonapi.routes/issues/49: Setting the ID throws a traceback
- https://github.com/collective/plone.jsonapi.routes/issues/48: Implement cut/copy/paste routes
- https://github.com/collective/plone.jsonapi.routes/issues/46: Route Provider `portal` throws TypeError
- https://github.com/collective/plone.jsonapi.routes/issues/47: ZCML directive to enable AdvancedQuery if installed


**ENHANCEMENTS**

- API actions to cut/copy/paste contents
- New route provider `plonesites`
- Support for catalog brain schema


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
