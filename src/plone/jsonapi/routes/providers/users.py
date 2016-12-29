# -*- coding: utf-8 -*-

import logging
from plone import api as ploneapi

from plone.jsonapi.routes.api import url_for
from plone.jsonapi.routes.exceptions import APIError
from plone.jsonapi.routes import add_plone_route as route

logger = logging.getLogger("plone.jsonapi.routes.users")


def get_user_info(username=None, short=True):
    """ return the user informations
    """

    # XXX: refactoring needed in this function

    user = None
    anon = ploneapi.user.is_anonymous()
    current = ploneapi.user.get_current()

    # no username, go and get the current user
    if username is None:
        user = current
    else:
        user = ploneapi.user.get(username)

    if not user:
        raise KeyError('User not found')

    info = {
        "id":       user.getId(),
        "username": user.getUserName(),
        "url":      url_for("plone.jsonapi.routes.users", username=user.getUserName())
    }

    # return base info
    if short or anon:
        return info

    # try to get extended infos
    pu = user.getUser()
    properties = {}
    if "mutable_properties" in pu.listPropertysheets():
        mp = pu.getPropertysheet("mutable_properties")
        properties = dict(mp.propertyItems())

    def to_iso8601(dt=None):
        if dt is None:
            return ""
        return dt.ISO8601()

    # include mutable properties if short==False
    info.update({
        "email":           properties.get("email"),
        "fullname":        properties.get("fullname"),
        "login_time":      to_iso8601(properties.get("login_time")),
        "last_login_time": to_iso8601(properties.get("last_login_time")),
        "roles":           user.getRoles(),
        "groups":          pu.getGroups(),
        "authenticated":   current == user and not anon,
    })

    return info


# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------

@route("/users", "plone.jsonapi.routes.users", methods=["GET"])
@route("/users/<string:username>", "plone.jsonapi.routes.users", methods=["GET"])
def get(context, request, username=None):
    """ Plone users route
    """

    items = []

    # don't allow anonymous to see other accounts
    if ploneapi.user.is_anonymous():
        username = "current"

    # list all users if no username was given
    if username is None:
        users = ploneapi.user.get_users()

        for user in users:
            items.append(get_user_info(user.getId()))

    # special user 'current' which retrieves the current user infos
    elif username == "current":
        items.append(get_user_info(short=False))

    # we have a username, go and get the infos for it
    else:
        info = get_user_info(username, short=False)
        items.append(info)

    return {
        "url":   url_for("plone.jsonapi.routes.users"),
        "count": len(items),
        "items": items
    }


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
        raise APIError(400, "__ac_name is missing")
    if __ac_password is None:
        raise APIError(400, "__ac_password is missing")

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
    return get(context, request, username=__ac_name)


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
