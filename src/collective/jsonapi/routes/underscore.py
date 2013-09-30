# -*- coding: utf-8 -*-

import types


def _isString(thing):
    return type(thing) in types.StringTypes

def _isList(thing):
    return type(thing) is types.ListType

def _isTuple(thing):
    return type(thing) is types.TupleType

def _isDict(thing):
    return type(thing) is types.DictType

def _isDigit(thing):
    return str(thing).isdigit()

def _pluck(lst, key):
    if not _isList(lst): return []
    def _block(dct):
        if not _isDict(dct): return []
        return dct.get(key)
    return filter(None, map(_block, lst))

# vim: set ft=python ts=4 sw=4 expandtab :
