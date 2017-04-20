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

The resource for folders is called `folder`.

We need to import the route providers for our test, so that the routes gets
registered::

    >>> from plone.jsonapi.routes.providers import *

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


A custom route provider can be easily created with the `add_plone_route`
decorator. In the next case, the route `hello/<string:name>` will be registered in the router
for the key `hello` and will be accessible on the API url `/@@API/plone/api/1.0/hello/<string:name>`::

    >>> from plone.jsonapi.routes import add_plone_route

    >>> @add_plone_route("/hello", "hello", methods=["GET"])
    ... @add_plone_route("/hello/<string:name>", "hello", methods=["GET"])
    ... def hello(context, request, name="world"):
    ...     return dict(hello=name)

    >>> browser.open(api_url + "/hello")
    >>> browser.contents
    '{"_runtime": ..., "hello": "world"}'

    >>> browser.open(api_url + "/hello/plone")
    >>> browser.contents
    '{"_runtime": ..., "hello": "plone"}'

Routes can not be registered twice with the same endpoint name. So registering
another route for the endpoint `hello` will fail::

#    >>> @add_plone_route("/hello2", "hello", methods=["GET"])
#    ... def hello(context, request, name="world"):
#    ...     return dict(hello=name)
#
#    >>> browser.open(api_url + "/hello2")
#    >>> browser.contents
#    '{"_runtime": ..., "message": "404: Not Found", "success": false}'

Route Providers can use the API of this package to search for contents in Plone::

    >>> from plone.jsonapi.routes.api import get_batched

    >>> @add_plone_route("/myroute", "myroute", methods=["GET"])
    ... @add_plone_route("/myroute/<string:uid>", "myroute", methods=["GET"])
    ... def myroute(context, request, uid=None):
    ...     return get_batched("Document", uid=uid)

    >>> browser.open(api_url + "/myroute")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    50

The API even accepts custom catalog queries::

    >>> @add_plone_route("/mycustom", "mycustom", methods=["GET"])
    ... def mycustom(context, request):
    ...     query = {"portal_type": "Document"}
    ...     return get_batched(query=query)

    >>> browser.open(api_url + "/mycustom")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    50

Keywords are applied to catalog indexes (only if no complete `query` parameter sent)::

    >>> @add_plone_route("/mycustom2", "mycustom2", methods=["GET"])
    ... def mycustom(context, request):
    ...     return get_batched(id="document-0")

    >>> browser.open(api_url + "/mycustom2")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    1


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

    >>> browser.open(api_url + "/search?portal_type=Document&sort_on=sortable_title")
    >>> response = self.decode(browser.contents)
    >>> [x['id'] for x in response.get('items')][:3]
    ['document-0', 'document-1', 'document-2']

We can also use 'descending' sort::

    >>> browser.open(api_url + "/search?portal_type=Document&sort_on=sortable_title&sort_order=descending")
    >>> response = self.decode(browser.contents)
    >>> [x['id'] for x in response.get('items')][:3]
    ['document-49', 'document-48', 'document-47']


Search
======

The `search` route can be used to search the `portal_catalog` for all kinds of
contents and returns the results batch-wise.

Let's search for `Documents` first::

    >>> browser.open(api_url + "/search?portal_type=Document")
    >>> response = self.decode(browser.contents)
    >>> len(response.get('items'))
    25
    >>> response.get('pages')
    2

Now we limt the search to 1. We should have 50 pages with 1 Document on each page::

    >>> browser.open(api_url + "/search?portal_type=Document&limit=1")
    >>> response = self.decode(browser.contents)
    >>> len(response.get('items'))
    1
    >>> response.get('pages')
    50

Try to find a Document with a specific title::

    >>> browser.open(api_url + "/search?portal_type=Document&Title=Document 10")
    >>> response = self.decode(browser.contents)
    >>> len(response.get('items'))
    1
    >>> response.get('pages')
    1
    >>> document = response.get('items')[0]
    >>> document.get('title')
    'Test Document 10'

Try to search for `Document` and `Folder` content types::

    >>> browser.open(api_url + "/search?portal_type=Document&portal_type=Folder&sort_on=getObjPositionInParent")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    51
    >>> response.get('pages')
    3
    >>> document = response.get('items')[0]
    >>> document.get('title')
    'Test Document 0'

Change to descending sort order, so the folder should appear first::

    >>> browser.open(api_url + "/search?portal_type=Document&portal_type=Folder&sort_order=descending&sort_on=sortable_title")
    >>> response = self.decode(browser.contents)
    >>> response.get('items')[0]['title']
    'Test Folder'

Make use of the `SearchableText` via the `q` request parameter::

    >>> browser.open(api_url + "/search?q=Test Document&sort_on=getObjPositionInParent")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    50
    >>> response.get('pages')
    2
    >>> [x['id'] for x in response.get('items')][:3]
    ['document-0', 'document-1', 'document-2']

    >>> browser.open(api_url + "/search?q=Test Folder")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    1
    >>> response.get('pages')
    1
    >>> [x['id'] for x in response.get('items')][:3]
    ['folder']

Make use of the  `recent_created` custom query::

    >>> browser.open(api_url + "/search?recent_created=today&sort_on=getObjPositionInParent")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    51
    >>> [x['id'] for x in response.get('items')][:3]
    ['document-0', 'document-1', 'document-2']

Make use of the `path` custom query with `depth`::

    >>> browser.open(api_url + "/search?path=/" + portal.id + "/folder&depth=1")
    >>> response = self.decode(browser.contents)
    >>> [x['id'] for x in response.get('items')][:3]
    ['document-0', 'document-1', 'document-2']


Search for Portal::

    >>> browser.open(api_url + "/search?portal_type=Plone Site")
    >>> response = self.decode(browser.contents)
    >>> response.get('count')
    1
    >>> response.get("items")[0]["uid"]
    '0'
    >>> response.get("items")[0]["id"]
    'plone'


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
