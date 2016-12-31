# -*- coding: utf-8 -*-

import logging
from plone import api as ploneapi

from plone.jsonapi.routes.api import url_for
from plone.jsonapi.routes.exceptions import APIError
from plone.jsonapi.routes import add_plone_route as route
from plone.jsonapi.routes.providers.users import get as get_user

logger = logging.getLogger("plone.jsonapi.routes.users")


@route("/auth", "plone.jsonapi.routes.auth", methods=["GET"])
def auth(context, request):
    """ Basic Authentication
    """

    if ploneapi.user.is_anonymous():
        request.response.setStatus(401)
        request.response.setHeader('WWW-Authenticate',
                                   'basic realm="JSONAPI AUTH"', 1)

    logger.info("*** BASIC AUTHENTICATE ***")
    return {}


@route("/login", "plone.jsonapi.routes.login", methods=["GET"])
def login(context, request):
    """ Login Route

    Login route to authenticate a user against Plone.
    """
    # extract the data
    __ac_name = request.form.get("__ac_name", None)
    __ac_password = request.form.get("__ac_password", None)

    logger.info("*** LOGIN %s ***" % __ac_name)

    if __ac_name is None:
        raise APIError(400, "Username is missing")
    if __ac_password is None:
        raise APIError(400, "Password is missing")

    acl_users = ploneapi.portal.get_tool("acl_users")

    # XXX hard coded
    acl_users.credentials_cookie_auth.login()

    # XXX amin user won't be logged in if I use this approach
    # acl_users.login()
    # response = request.response
    # acl_users.updateCredentials(request, response, __ac_name, __ac_password)

    if ploneapi.user.is_anonymous():
        raise APIError(401, "Invalid Credentials")

    # return the JSON in the same format like the user route
    return get_user(context, request, username=__ac_name)


@route("/logout", "plone.jsonapi.routes.logout", methods=["GET"])
def logout(context, request):
    """ Logout Route
    """
    logger.info("*** LOGOUT ***")

    acl_users = ploneapi.portal.get_tool("acl_users")
    acl_users.logout(request)

    return {
        "url":     url_for("plone.jsonapi.routes.users"),
        "success": True
    }
