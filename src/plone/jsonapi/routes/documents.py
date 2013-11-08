# -*- coding: utf-8 -*-

from plone.jsonapi.core import router

from api import url_for
from api import get_items


# HTTP GET
@router.add_route("/documents", "documents", methods=["GET"])
@router.add_route("/documents/<string:uid>", "documents", methods=["GET"])
def documents(context, request, uid=None):
    """ get documents
    """
    items = get_items("Document", request, uid=uid, endpoint="documents")
    return {
        "url": url_for("documents"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
