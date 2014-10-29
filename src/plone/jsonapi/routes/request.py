# -*- coding: utf-8 -*-

__author__    = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'

import json
import logging

from zope.globalrequest import getRequest

from plone.jsonapi.routes import underscore as _

logger = logging.getLogger("plone.jsonapi.routes.request")


def get_request():
    """ return the request object
    """
    return getRequest()


def get_complete():
    """ returns the 'complete' from the request
    """
    request = get_request()
    complete = request.form.get("complete", "no")
    if complete.lower() in ["y", "yes", "1", "true"]:
        return True
    return False


def get_children():
    """ returns the 'children' from the request
    """
    request = get_request()
    complete = request.form.get("children", "no")
    if complete.lower() in ["y", "yes", "1", "true"]:
        return True
    return False


def get_sort_limit():
    """ returns the 'sort_limit' from the request
    """
    request = get_request()
    limit = _.convert(request.form.get("sort_limit"), _.to_int)
    if (limit < 1): limit = None # catalog raises IndexError if limit < 1
    return limit


def get_batch_size():
    """ returns the 'limit' from the request
    """
    request = get_request()
    return _.convert(request.form.get("limit"), _.to_int) or 25


def get_batch_start():
    """ returns the 'start' from the request
    """
    request = get_request()
    return _.convert(request.form.get("b_start"), _.to_int) or 0


def get_sort_on(allowed_indexes=None):
    """ returns the 'sort_on' from the request
    """
    request = get_request()
    sort_on = request.form.get("sort_on")
    if allowed_indexes and sort_on not in allowed_indexes:
        logger.warn("Index '%s' is not in allowed_indexes" % sort_on)
        return "id"
    return sort_on


def get_sort_order():
    """ returns the 'sort_order' from the request
    """
    request = get_request()
    sort_order = request.form.get("sort_order")
    if sort_order in ["ASC", "ascending", "a", "asc", "up", "high"]:
        return "ascending"
    if sort_order in ["DESC", "descending", "d", "desc", "down", "low"]:
        return "descending"
    return "descending"


def get_query():
    """ returns the 'query' from the request
    """
    request = get_request()
    q = request.form.get("q", "")

    qs = q.lstrip("*.!$%&/()=#-+:'`´^")
    if qs and not qs.endswith("*"):
        qs += "*"
    return qs


def get_path():
    """ returns the 'path' from the request
    """
    request = get_request()
    return request.form.get("path", "")


def get_depth():
    """ returns the 'depth' from the request
    """
    request = get_request()
    return  _.convert(request.form.get("depth", 0), _.to_int)


def get_recent_created():
    """ returns the 'recent_created' from the request
    """
    request = get_request()
    return request.form.get("recent_created", None)


def get_recent_modified():
    """ returns the 'recent_modified' from the request
    """
    request = get_request()
    return request.form.get("recent_modified", None)


def get_request_data():
    """ extract and convert the json data from the request

    returns a list of dictionaries
    """
    request = get_request()
    return _.convert(json.loads(request.get("BODY", "{}")), _.to_list)

# vim: set ft=python ts=4 sw=4 expandtab :
