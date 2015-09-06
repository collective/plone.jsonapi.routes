# -*- coding: utf-8 -*-

from plone.jsonapi.routes import api
from plone.jsonapi.routes.api import url_for
from plone.jsonapi.routes import request as req
from plone.jsonapi.routes import add_plone_route as route
from plone.jsonapi.routes.exceptions import APIError


# CUT
@route("/cut", "cut", methods=["GET"])
@route("/cut/<string:uid>", "cut", methods=["GET"])
def cut(context, request, uid=None):
    """ cut content
    """
    obj = None

    if uid is not None:
        obj = api.get_object_by_uid(uid)

    if obj is None:
        raise APIError(400, "No object found with UID %s" % uid)
    if api.is_root(obj):
        raise APIError(400, "Not allowed to cut the whole Portal")

    # cut the object
    obj.aq_parent.manage_cutObjects(obj.getId(), REQUEST=request)

    # extract the response cookie
    result = request.response.cookies.get("__cp")

    return {
        "url": url_for("cut", uid=uid),
        "uid": uid,
        "success": result is not None
    }


# COPY
@route("/copy", "copy", methods=["GET"])
@route("/copy/<string:uid>", "copy", methods=["GET"])
def copy(context, request, uid=None):
    """ copy content
    """
    obj = None

    if uid is not None:
        obj = api.get_object_by_uid(uid)

    if obj is None:
        raise APIError(400, "No object found with UID %s" % uid)
    if api.is_root(obj):
        raise APIError(400, "Not allowed to copy the whole Portal")

    # copy the object
    obj.aq_parent.manage_copyObjects(obj.getId(), REQUEST=request)

    # extract the response cookie
    result = request.response.cookies.get("__cp")

    return {
        "url": url_for("copy", uid=uid),
        "uid": uid,
        "success": result is not None
    }


# PASTE
@route("/paste", "paste", methods=["GET"])
@route("/paste/<string:uid>", "paste", methods=["GET"])
def paste(context, request, uid=None):
    """ paste content
    """
    obj = None

    if uid is not None:
        obj = api.get_object_by_uid(uid)

    if obj is None:
        raise APIError(400, "No object found with UID %s" % uid)

    cookie = req.get_cookie("__cp")
    if cookie is None:
        raise APIError(400, "No data found in clipboard")

    # paste the object
    obj.manage_pasteObjects(cookie, REQUEST=request)

    return {
        "url": url_for("copy", uid=uid),
        "uid": uid,
        "success": True
    }
