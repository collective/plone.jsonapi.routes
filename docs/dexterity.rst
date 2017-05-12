Dexterity Content
=================

.. versionadded:: 0.7
    Added Dexterity Data Manager (see: datamanagers.py)

.. versionadded:: 0.9.2
    Added Zope Schema Field Manager (see: fieldmanagers.py)

Dexterity Content Types are handled by a Data Manager (`IDataManager`) and a
Field Manager (`IFieldManager`) respectively. Also see :ref:`DATA_MANAGER`.
Integrators just have to add route providers for their Dexterity Content Types
(see: :ref:`ROUTE_PROVIDER`) and the JSON API should handle the heavy lifting.


Security
--------

`plone.jsonapi.routes` checks only the permission on the content object to be
at least `cmf.ModifyPortalContent`. Checks on the field level will be added in
future versions.
