# -*- coding: utf-8 -*-

from plone import api as ploneapi

from plone.jsonapi.routes import add_plone_route
from plone.jsonapi.routes.api import url_for


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
        "url":      url_for("users", username=user.getUserName())
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


#-----------------------------------------------------------------------------
# API ROUTES
#-----------------------------------------------------------------------------

@add_plone_route("/users", "users", methods=["GET"])
@add_plone_route("/users/<string:username>", "users", methods=["GET"])
def get(context, request, username=None):
    """ NSK users route
    """

    items = []

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
        "url":   url_for("users"),
        "count": len(items),
        "items": items
    }

# vim: set ft=python ts=4 sw=4 expandtab :
