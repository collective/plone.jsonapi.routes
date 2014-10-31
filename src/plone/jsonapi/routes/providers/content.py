# -*- coding: utf-8 -*-

from plone.jsonapi.routes import add_plone_route

from plone.jsonapi.routes.api import get_record


# GET
@add_plone_route("/<string:uid>", "content", methods=["GET"])
def get(context, request, uid=0):
    """ get node by uid
    """
    return get_record(uid=uid)

# vim: set ft=python ts=4 sw=4 expandtab :
