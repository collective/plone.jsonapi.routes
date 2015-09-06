Quickstart
==========

This section gives a good introduction about `plone.jsonapi.routes` It assumes
you already have `Plone` and `plone.jsonapi.routes` installed. Since all the
coming examples are executed directly in Google Chrome, it assumes that you
have also installed JSONView and the Advanced Rest Client Application (see
:doc:`installation` for details)


Environment
-----------

The Plone site is hosted on `http://localhost:8080/Plone`. The JSON API is thus
located at `http://localhost:8080/Plone/@@API/plone/api/1.0`. Make sure your Plone
site is located on the same URL, so you can directly click on the links within the
exapmles.


Version
-------

The `version` route prints out the current version of `plone.jsonapi.routes`.

http://localhost:8080/Plone/@@API/plone/api/1.0/version

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/version",
        date: "2014-12-21",
        version: "0.4",
        build: 200,
        _runtime: 0.0001528865814208984
    }


Overview
--------

The `api.json` route gives you an overview over all registered routes.

http://localhost:8080/Plone/@@API/plone/api/1.0/api.json

.. code-block:: javascript

    {
        url: "http://localhost:8080/Plone/@@API/plone/api/1.0/api.json",
        count: 11,
        _runtime: 0.0027348995208740234,
        items: [
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/collections",
                info: "get collections",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents",
                info: "No description available",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/newsitems",
                info: "get newsitems",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/folders",
                info: "get folders",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/version",
                info: "get the current version of this package",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/events",
                info: "get events",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/images",
                info: "get images",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/topics",
                info: "get topics",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/files",
                info: "get files",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/links",
                info: "get links",
                methods: "HEAD,GET"
            },
            {
                url: "http://localhost:8080/Plone/@@API/plone/api/1.0/users",
                info: "Plone users route",
                methods: "HEAD,GET"
            }
        ]
    }


Content Routes
--------------

Coming now to a more interesting section, the `content routes`. These
:ref:`Resources` represent the data of the standard Plone content types.

Each resource is located at the :ref:`BASE_URL`, e.g.

http://localhost:8080/Plone/@@API/plone/api/1.0/folders

The following sections describe each resource in detail.


Documents
---------

The `documents` route will rule all contents of the portal type `Document`.

http://localhost:8080/Plone/@@API/plone/api/1.0/documents

.. code-block:: javascript

    {
        count: 1,
        pagesize: 25,
        items: [
            {
                uid: "7455c9b14e3c48c9b0be19ca6a142d50",
                tags: [ ],
                portal_type: "Document",
                id: "front-page",
                description: "Herzlichen Glückwunsch! Sie haben das professionelle Open-Source Content-Management-System Plone erfolgreich installiert.",
                api_url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/7455c9b14e3c48c9b0be19ca6a142d50",
                effective: "1000-01-01T00:00:00+02:00",
                title: "Willkommen bei Plone",
                url: "http://localhost:8080/Plone/front-page",
                created: "2014-10-14T20:22:19+02:00",
                modified: "2014-10-14T20:22:19+02:00",
                type: "Document"
            }
        ],
        page: 1,
        _runtime: 0.0038590431213378906,
        next: null,
        pages: 1,
        previous: null
    }

The :ref:`Response_Format` in `plone.jsonapi.routes` content URLs is always
the same.  The top level keys (data after the first ``{``) are meta
informations about the gathered data.

Within the **items** list, you get all the results listed. It is important to
know, that these records contain only the minimum set of data from the catalog
brains. This is because of the APIs **two step** concept, which postpones
expensive opreations, until the user really wants it.

.. versionadded:: 0.3
    The result is now always batched. This means you get
    the items split up into batches onto multiple sites.


Getting all the data
~~~~~~~~~~~~~~~~~~~~

To get all data from the object, you can either add the ``complete=True`` parameter,
or you can request the data with the object ``UID``.

http://localhost:8080/Plone/@@API/plone/api/1.0/documents?complete=True

http://localhost:8080/Plone/@@API/plone/api/1.0/documents/7455c9b14e3c48c9b0be19ca6a142d50

.. note:: The UID will probably be different on your machine.


.. code-block:: javascript

    {
        count: 1,
        pagesize: 25,
        items: [
            {
                uid: "7455c9b14e3c48c9b0be19ca6a142d50",
                contributors: [ ],
                tags: [ ],
                text: "<p class="discreet">Wenn Sie diese Seite anstelle des von Ihnen erwarteten Inhalts sehen, hat der Betreiber dieser Website gerade erst Plone installiert. Bitte benachrichtigen Sie NICHT das Plone Team, sondern den Betreiber dieser Website.</p><h2>So starten Sie!</h2><p>Bevor Sie sich mit Ihrer neuen Plone-Website vertraut machen, stellen Sie bitte sicher, dass</p><ol> <li>Sie als Administrator angemeldet sind. <span class="discreet">(Sie müssten im Menü oben rechts den Eintrag 'Konfiguration' finden.)</span></li> <li><a href="http://localhost:8080/Plone/@@mail-controlpanel">Sie den E-Mail-Dienst konfiguriert haben</a>. <span class="discreet">(Plone benötigt einen SMTP-Server zur Benutzerregistrierung und um Benutzern die Möglichkeit zu geben, ein vergessenes Passwort neu zu setzen.)</span></li> <li><a href="http://localhost:8080/Plone/@@security-controlpanel">Sie wissen, welche Sicherheitseinstellungen für Ihre Website gültig sind</a>. <span class="discreet">(Das betrifft zum Beispiel die Selbstregistrierung und das Setzen von Passwörtern)</span></li></ol><h2>Machen Sie sich mit Plone vertraut!</h2><p>Anschließend empfehlen wir Ihnen Folgendes:</p><ul> <li>Lesen Sie, <a class="link-plain" href="http://plone.org/documentation/whatsnew">welche neuen Funktionen Plone</a> enthält (in Englisch),</li> <li>Lesen Sie die <a class="link-plain" href="http://plone.org/documentation">Dokumentation</a> (in Englisch), insbesondere <a class="link-plain" href="http://plone.org/documentation/phc_topic_area?topic=Basic+Use">die grundlegenden Kapitel</a> und <a class="link-plain" href="http://plone.org/documentation/faq/server-recommendations">die Empfehlungen zur Server-Konfiguration</a>. </li> <li>Lernen Sie die grundlegenden <a href="http://www.hasecke.com/plone-white-paper">Leistungsmerkmale</a> von Plone kennen.</li> <li>Lesen Sie das deutschsprachige <a href="http://www.hasecke.com/plone-benutzerhandbuch/">Plone-Benutzerhandbuch</a>.</li> <li>Nutzen Sie das deutschsprachige <a href="http://www.plone-entwicklerhandbuch.de">Plone-Entwicklerhandbuch</a>, wenn Sie Erweiterungen für Plone programmieren möchten.</li> <li>Entdecken Sie <a class="link-plain" href="http://plone.org/products">die verfügbaren Erweiterungen</a> für Plone.</li> <li>Lesen oder abonnieren Sie <a class="link-plain" href="http://plone.org/support">die englischsprachigen</a> oder <a class="link-plain" href="https://mail.dzug.org/mailman/listinfo/zope">die deutschsprachigen Mailinglisten</a>.</li></ul><h2>Individualisieren Sie Plone!</h2><p>Plone kann sehr individuell konfiguriert werden. Hier einige Beispiele:</p><ul> <li> Wählen Sie unter den <a href="http://localhost:8080/Plone/@@skins-controlpanel">installierten Designs</a> ein neues aus, oder installieren Sie <a class="link-plain" href="http://plone.org/products/by-category/themes">eins der verfügbaren Designs von plone.org</a>. <span class="discreet">(Bitte stellen Sie sicher, dass das Design mit der Plone-Version, die Sie installiert haben, kompatibel ist)</span> </li> <li> <a href="http://localhost:8080/Plone/@@types-controlpanel"> Bestimmen Sie die Arbeitsabläufe in Ihrer Website.</a> <span class="discreet">(Standardmäßig ist ein Arbeitsablauf für öffentliche Websites eingestellt, wenn Sie Plone als geschlossenes Intranet betreiben wollen, können Sie den Arbeitsablauf entsprechend ändern.)</span> </li> <li> Standardmäßig bearbeiten Sie die Inhalte mit einem visuellem Texteditor. <span class="discreet">(Wenn Sie eine textbasierte Syntax oder Wiki-Markup bevorzugen, können Sie dies in den <a href="http://localhost:8080/Plone/@@markup-controlpanel">Einstellungen für Textauszeichnung</a> auswählen)</span> </li> <li>Weitere Optionen stehen Ihnen in der <a href="http://localhost:8080/Plone/plone_control_panel">Website-Konfiguration</a> zur Verfügung. </li></ul><h2>Sagen Sie uns, wie Sie Plone nutzen!</h2><p>Haben Sie mit Plone etwas Interessantes vor? Möchten Sie eine große Website betreiben,oder haben Sie einen außergewöhnlichen Anwendungsfall? Bieten Sie als Unternehmen Lösungen auf Basis von Plone an?</p><ul> <li>Tragen Sie Ihr Unternehmen in die Liste der <a class="link-plain" href="http://plone.net/providers">Plone Dienstleister</a> ein.</li> <li>Tragen Sie Ihre Website in die Liste der <a class="link-plain" href="http://plone.net/sites">Plone Websites</a> ein. <span class="discreet">(Entdecken Sie, welche Websites bereits mit Plone betrieben werden!)</span> </li> <li>Beschreiben Sie in einer <a class="link-plain" href="http://plone.net/case-studies">Fallstudie</a> Ihr Projekt und Ihren Kunden.</li></ul><h2>Lernen Sie mehr über die Software-Architektur!</h2><p>Plone ist eine Anwendung für den Zope Applikationsserver und wurde in der objektorientierten Programmiersprache Python entwickelt. Mehr über diese Technologien erfahren Sie:</p><ul><li>auf der Website der <a class="link-plain" href="http://plone.org">Plone Community </a></li><li>auf der Website für den <a class="link-plain" href="http://zope2.zope.org">Zope Applikationsserver</a></li><li>auf der Website der <a class="link-plain" href="http://www.python.org">Python-Community</a>. </li></ul><h2>Spenden Sie an die Plone Foundation!</h2><p>Zahllose engagierte Personen und Unternehmen haben Plone möglich gemacht. Die Plone Foundation:</p><ul> <li>...schützt und unterstützt Plone,</li> <li>...ist eine gemeinnützige Organisation nach dem US-Gesetz 501(c)(3) und</li> <li>...kann Spendenquittungen ausstellen.</li></ul> <p><a href="http://plone.org/foundation/foundation-donations">Helfen Sie mit!</a></p><p>Danke, dass Sie Plone einsetzen. Wir hoffen, dass Sie begeistert sein werden!</p><p>Ihr Plone-Team</p>",
                portal_type: "Document",
                subject: [ ],
                creation_date: "2014-10-14T20:22:19+02:00",
                language: "de",
                creators: [
                    "admin"
                ],
                expirationDate: null,
                tableContents: false,
                id: "front-page",
                description: "Herzlichen Glückwunsch! Sie haben das professionelle Open-Source Content-Management-System Plone erfolgreich installiert.",
                parent_id: "Plone",
                rights: "",
                api_url: "http://localhost:8080/Plone/@@API/plone/api/1.0/documents/7455c9b14e3c48c9b0be19ca6a142d50",
                effective: "1000-01-01T00:00:00+02:00",
                title: "Willkommen bei Plone",
                url: "http://localhost:8080/Plone/front-page",
                presentation: true,
                created: "2014-10-14T20:22:19+02:00",
                modified: "2014-10-14T20:22:19+02:00",
                parent_uid: 0,
                modification_date: "2014-10-14T20:22:19+02:00",
                effectiveDate: null,
                relatedItems: [ ],
                location: "",
                allowDiscussion: false,
                excludeFromNav: false,
                type: "Document",
                workflow_info: {
                status: "Published",
                review_state: "published",
                transitions: [
                    {
                        url: "http://localhost:8080/Plone/front-page/content_status_modify?workflow_action=retract",
                        display: "If you submitted the item by mistake or want to perform additional edits, this will take it back.",
                        value: "retract"
                    },
                    {
                        url: "http://localhost:8080/Plone/front-page/content_status_modify?workflow_action=reject",
                        display: "Sending the item back will return the item to the original author instead of publishing it. You should preferably include a reason for why it was not published.",
                        value: "reject"
                    }
                ],
                workflow: "simple_publication_workflow"
                }
            }
        ],
        page: 1,
        _runtime: 0.15096807479858398,
        next: null,
        pages: 1,
        previous: null
    }

The requested object was now loaded by the API and all fields were gathered.
But not all data is coming directly from the object fields. Some of them have
been augmented by the API, such as ``transitions``.

.. note:: Please keep in mind that large data sets with the `?complete=True`
          Parameter might increase the loading time significantly.


Folders
-------

The `folders` route will rule all contents of the portal type `Folder`.

http://localhost:8080/Plone/@@API/plone/api/1.0/folders


Events
------

The `events` route will rule all contents of the portal type `Events`.

http://localhost:8080/Plone/@@API/plone/api/1.0/events


Files
-----

The `files` route will rule all contents of the portal type `File`.

http://localhost:8080/Plone/@@API/plone/api/1.0/files

.. versionadded:: 0.2
    The object data contains now the base64 encoded file with the size and
    mimetype information.

.. versionadded:: 0.7
    You can pass in a `filename` in the JSON body to set the name of the file
    created. If omitted, the id or title will be used.

.. versionadded:: 0.8
    You can pass in a `mimetype` key to manually set the content type of the
    file. If omitted, the content type will be guessed by the filename.
    Default: `application/octet-stream`

.. versionadded:: 0.8
    The response data contains now the `filename` and the `download` url.

Example
.......

To create a new file in the portal, you have to append `create` to the route.

http://localhost:8080/Plone/@@API/plone/api/1.0/files/create

The POST payload can look like this:

.. code-block:: javascript

    {
        "title": "Test.docx",
        "description": "A Word File",
        "filename": "test.docx",
        "parent_path": "/Plone/folder",
        "file":"UEsDBBQABgAIAAA..."
    }


Images
------

The `images` route will rule all contents of the portal type `Image`.

http://localhost:8080/Plone/@@API/plone/api/1.0/images

.. versionadded:: 0.2
    The object data contains now the base64 encoded image with the size and
    mimetype information.

.. versionadded:: 0.8
    The response data contains now the `filename` and the `download` url.

Links
-----

The `links` route will rule all contents of the portal type `Link`.

http://localhost:8080/Plone/@@API/plone/api/1.0/links


News Items
----------

The `newsitems` route will rule all contents of the portal type `News Item`.

http://localhost:8080/Plone/@@API/plone/api/1.0/newsitems


Topics
------

The `topics` route will rule all contents of the portal type `Topic`.

http://localhost:8080/Plone/@@API/plone/api/1.0/topics


Collections
-----------

The `collections` route will rule all contents of the portal type `Collection`.

http://localhost:8080/Plone/@@API/plone/api/1.0/collections
