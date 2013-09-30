# -*- coding: utf-8 -*-

from plone.jsonapi import router

from Products.ATContentTypes.interfaces import IATDocument

from api import *


# GET
@router.add_route("/documents", "documents", methods=["GET"])
@router.add_route("/documents/<string:uid>", "documents", methods=["GET"])
def documents(context, request, uid=None):
    """ get documents
    """
    items = get_contents(IATDocument, request, uid=uid)
    items = [get_base_info(item, "documents") for item in items]

    return {
        "url": url_for("documents"),
        "count": len(items),
        "items": items,
    }

# vim: set ft=python ts=4 sw=4 expandtab :
