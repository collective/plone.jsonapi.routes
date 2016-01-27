# -*- coding: utf-8 -*-

import json
import logging
import pkg_resources

from zope import interface

from zope.globalrequest import getRequest

try:
    pkg_resources.get_distribution('plone.protect')
    from plone.protect.interfaces import IDisableCSRFProtection
except (pkg_resources.DistributionNotFound, ImportError):
    HAS_PLONE_PROTECT = False
else:
    HAS_PLONE_PROTECT = True

from plone.jsonapi.routes import underscore as _

__author__ = 'Ramon Bartl <ramon.bartl@googlemail.com>'
__docformat__ = 'plaintext'


# These values evaluate to True
TRUE_VALUES = ["y", "yes", "1", "true", True]

logger = logging.getLogger("plone.jsonapi.routes.request")


def get_request():
    """ return the request object
    """
    return getRequest()


def disable_csrf_protection():
    """ disables the CSRF protection
        https://pypi.python.org/pypi/plone.protect
    """
    if not HAS_PLONE_PROTECT:
        logger.warn(
            "Can not disable CSRF protection – please install plone.protect"
        )
        return False
    request = get_request()
    interface.alsoProvides(request, IDisableCSRFProtection)
    return True


def get_form():
    """ return the request form dictionary
    """
    return get_request().form


def get(key, default=None):
    """ return the key from the request
    """
    return get_form().get(key, default)


def is_true(key, default=False):
    ''' Check if the value is in TRUE_VALUES
    '''
    value = get(key, default)
    if isinstance(value, list):
        value = value[0]
    if isinstance(value, bool):
        return value
    if value is default:
        return default
    return value.lower() in TRUE_VALUES


def get_cookie(key, default=None):
    """ return the key from the request
    """
    return get_request().cookies.get(key, default)


def get_complete(default=None):
    """ returns the 'complete' from the request
    """
    return is_true("complete", default)


def get_children(default=None):
    """ returns the 'children' from the request
    """
    return is_true("children", default)


def get_filedata(default=None):
    """ returns the 'filedata' from the request
    """
    return is_true('filedata')


def get_workflow(default=None):
    """ returns the 'workflow' from the request
    """
    return is_true("workflow", default)


def get_sharing(default=None):
    """ returns the 'sharing' from the request
    """
    return is_true("sharing", default)


def get_sort_limit():
    """ returns the 'sort_limit' from the request
    """
    limit = _.convert(get("sort_limit"), _.to_int)
    if (limit < 1):
        limit = None  # catalog raises IndexError if limit < 1
    return limit


def get_batch_size():
    """ returns the 'limit' from the request
    """
    return _.convert(get("limit"), _.to_int) or 25


def get_batch_start():
    """ returns the 'start' from the request
    """
    return _.convert(get("b_start"), _.to_int) or 0


def get_sort_on(allowed_indexes=None):
    """ returns the 'sort_on' from the request
    """
    sort_on = get("sort_on")
    if allowed_indexes and sort_on not in allowed_indexes:
        logger.warn("Index '%s' is not in allowed_indexes" % sort_on)
        return "id"
    return sort_on


def get_sort_order():
    """ returns the 'sort_order' from the request
    """
    sort_order = get("sort_order")
    if sort_order in ["ASC", "ascending", "a", "asc", "up", "high"]:
        return "ascending"
    if sort_order in ["DESC", "descending", "d", "desc", "down", "low"]:
        return "descending"
    # https://github.com/collective/plone.jsonapi.routes/issues/31
    return "ascending"


def get_query():
    """ returns the 'query' from the request
    """
    q = get("q", "")

    qs = q.lstrip("*.!$%&/()=#-+:'`´^")
    if qs and not qs.endswith("*"):
        qs += "*"
    return qs


def get_path():
    """ returns the 'path' from the request
    """
    return get("path", "")


def get_depth():
    """ returns the 'depth' from the request
    """
    return _.convert(get("depth", 0), _.to_int)


def get_recent_created():
    """ returns the 'recent_created' from the request
    """
    return get("recent_created", None)


def get_recent_modified():
    """ returns the 'recent_modified' from the request
    """
    return get("recent_modified", None)


def get_request_data():
    """ extract and convert the json data from the request

    returns a list of dictionaries
    """
    request = get_request()
    return _.convert(json.loads(request.get("BODY", "{}")), _.to_list)


def get_json():
    """ get the request json payload
    """
    data = get_request_data().pop()
    return data or dict()


def get_json_key(key, default=None):
    """ return the key from the json payload
    """
    return get_json().get(key, default)


def set_json_item(key, value):
    """ manipulate json data on the fly
    """
    data = get_json()
    data[key] = value

    request = get_request()
    request["BODY"] = json.dumps(data)
