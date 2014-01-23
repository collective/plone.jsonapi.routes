# -*- coding: utf-8 -*-

import json

import underscore as _


def get_sort_limit(request):
    """ returns the 'sort_limit' from the request
    """
    limit = _.convert(request.form.get("limit"), _.to_int)
    if (limit < 1): limit = None # catalog raises IndexError if limit < 1
    return limit

def get_start(request):
    """ returns the 'start' from the request
    """
    return _.convert(request.form.get("start"), _.to_int)

def get_sort_on(request, allowed_indexes=None):
    """ returns the 'sort_on' from the request
    """
    sort_on = request.form.get("sort_on")
    if allowed_indexes and sort_on not in allowed_indexes:
        _.fail("Usage of index '%s' is not allowed." % sort_on)
    return sort_on

def get_sort_order(request):
    """ returns the 'sort_order' from the request
    """
    sort_order = request.form.get("sort_order")
    if sort_order in ["ascending", "a", "asc", "up", "high"]:
        return "ascending"
    if sort_order in ["descending", "d", "desc", "down", "low"]:
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

def get_creator(request):
    """ returns the 'creator' from the request
    """
    return request.form.get("creator", "")

def get_request_data(request):
    """ extract and convert the json data from the request

        >>> request = dict(BODY="{}")
        >>> get_request_data(request)
        [{}]
    """
    return _.convert(json.loads(request.get("BODY", {})), _.to_list)


if __name__ == '__main__':
    import doctest
    doctest.testmod(raise_on_error=False, optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

# vim: set ft=python ts=4 sw=4 expandtab :
