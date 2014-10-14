# -*- coding: utf-8 -*-

import json
import logging

from plone.jsonapi.routes import underscore as _

logger = logging.getLogger("plone.jsonapi.routes.request")


def get_uid(request):
    """ returns the 'uid' from the request
    """
    return request.form.get("uid")


def get_complete(request):
    """ returns the 'complete' from the request
    """
    complete = request.form.get("complete", "no")
    if complete.lower() in ["y", "yes", "1", "true"]:
        return True
    return False


def get_parent_uid(request):
    """ returns the 'parent_uid' from the request
    """
    return request.form.get("parent_uid")


def get_sort_limit(request):
    """ returns the 'sort_limit' from the request
    """
    limit = _.convert(request.form.get("sort_limit"), _.to_int)
    if (limit < 1): limit = None # catalog raises IndexError if limit < 1
    return limit


def get_batch_size(request):
    """ returns the 'limit' from the request
    """
    return _.convert(request.form.get("limit"), _.to_int) or 25


def get_batch_start(request):
    """ returns the 'start' from the request
    """
    return _.convert(request.form.get("b_start"), _.to_int) or 0


def get_sort_on(request, allowed_indexes=None):
    """ returns the 'sort_on' from the request
    """
    sort_on = request.form.get("sort")
    if allowed_indexes and sort_on not in allowed_indexes:
        logger.warn("Index '%s' is not in allowed_indexes" % sort_on)
        return "id"
    return sort_on


def get_sort_order(request):
    """ returns the 'sort_order' from the request
    """
    sort_order = request.form.get("dir")
    if sort_order in ["ASC", "ascending", "a", "asc", "up", "high"]:
        return "ascending"
    if sort_order in ["DESC", "descending", "d", "desc", "down", "low"]:
        return "descending"
    return "descending"


def get_query(request):
    """ returns the 'query' from the request
    """
    q = request.form.get("q", "")

    qs = q.lstrip("*.!$%&/()=#-+:'`´^")
    if qs and not qs.endswith("*"):
        qs += "*"
    return qs


def get_path(request):
    """ returns the 'path' from the request
    """
    return request.form.get("path", "")


def get_depth(request):
    """ returns the 'depth' from the request
    """
    return  _.convert(request.form.get("depth", 0), _.to_int)


def get_request_data(request):
    """ extract and convert the json data from the request

    returns a list of dictionaries
    """
    return _.convert(json.loads(request.get("BODY", {})), _.to_list)

# vim: set ft=python ts=4 sw=4 expandtab :
