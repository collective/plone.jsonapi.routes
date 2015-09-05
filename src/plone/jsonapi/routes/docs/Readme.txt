======================================
Plone JSONAPI Routes Integration Tests
======================================

With `plone.jsonapi.routes` enabled, it is simple to expose informations of
standard Plone content types.

Some needed imports::

    >>> from plone.jsonapi.routes.version import version

Prepare the browser::

    >>> portal = self.getPortal()
    >>> browser = self.getBrowser()
    >>> browser.addHeader('Authorization', 'Basic admin:secret')

Remember some URLs::

    >>> portal_url = portal.absolute_url()
    >>> api_url = portal_url + "/@@API/plone/api/1.0"
    >>> version_url = api_url + "/version"

Check if the version URL returns the right version::

    >>> browser.open(version_url)
    >>> dct = self.decode(browser.contents)
    >>> dct["url"] == version_url
    True
    >>> dct["version"] == version()
    True


Route Providers
================

The package provides for each contenttype a separate resource URL.
The next tests will go through each resource to show the basic usage.

Folders
-------

The resource for folders is called `folders`.

We need to import the module for our test, so that the route gets registered::

    >>> from plone.jsonapi.routes.providers import folders

Lets check if we have some folders in our portal::

    >>> browser.open(api_url + "/folders")
    >>> response = self.decode(browser.contents)

We expect **one** folder in our portal::

    >>> response.get("count")
    1

    >>> folder = response.get("items")[0]
    >>> folder.get("id") == "folder"
    True

    >>> folder.get("title") == "Test Folder"
    True


Query records
=============

ZPublisher query record format can be used for querying.
We test this with a simple created since query::

    >>> from urllib import urlencode
    >>> from datetime import datetime
    >>> from datetime import timedelta

    >>> now = datetime.now()
    >>> since_now = urlencode({
    ...    'created.query:record:list:date': now,
    ...    'created.range:record': 'min'})
    >>> browser.open(api_url + "/folders?" + since_now)
    >>> response = self.decode(browser.contents)

    >>> yesterday = now - timedelta(days=1)
    >>> since_yesterday = urlencode({
    ...     'created.query:record:list:date': yesterday,
    ...     'created.range:record': 'min'})
    >>> browser.open(api_url + "/folders?" + since_yesterday)
    >>> response = self.decode(browser.contents)

One folder created since yesterday - if not, we need to look at testrunner
performance ;-) ::

   >>> response.get("count")
   1


Sorting queries
===============

Queries accept standard `sort_order` and `sort_on` params.
Like the portal_catalog default, the default is ascending order.

    >>> browser.open(api_url + "/search?sort_on=sortable_title")
    >>> response = self.decode(browser.contents)
    >>> [x['id'] for x in response.get('items')][:3]
    ['document-0', 'document-1', 'document-2']

We can also use 'descending' sort::

    >>> browser.open(api_url + "/search?sort_on=sortable_title&sort_order=descending")
    >>> response = self.decode(browser.contents)
    >>> [x['id'] for x in response.get('items')][:3]
    ['folder', 'document-49', 'document-48']


Results data
============

What's in the result?

All catalog indexes are included in results, including any custom indexes::

    >>> browser.open(api_url + "/folders")
    >>> response = self.decode(browser.contents)
    >>> folder = response.get("items")[0]
    >>> keys = folder.keys()

The following default metadata columns are not included, since they duplicate
other indexes or are not really interesting outside plone::

    >>> ignored_metadata = [
    ...     'CreationDate',
    ...     'Creator',
    ...     'Date',
    ...     'Description',
    ...     'EffectiveDate',
    ...     'ExpirationDate',
    ...     'ModificationDate',
    ...     'Subject',
    ...     'Title',
    ...     'Type',
    ...     'UID',
    ...     'cmf_uid',
    ...     'getIcon',
    ...     'getId',
    ...     'getObjSize',
    ...     'getRemoteUrl',
    ...     'listCreators',
    ...     'meta_type',
    ... ]
    >>> filter(lambda k: k in ignored_metadata, keys)
    []

Some builtin metadata columns are mapped to simplified, lowercase keys::

    >>> mapped_metadata = ['id', 'uid', 'title', 'description', 'url', 'tags']
    >>> filter(lambda k: k in keys, mapped_metadata)
    ['id', 'uid', 'title', 'description', 'url', 'tags']

Custom indexes are included

    >>> folder['title_or_id']
    'Test Folder'
