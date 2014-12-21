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


Reoute Providers
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

.. vim: set ft=rst ts=4 sw=4 expandtab :
