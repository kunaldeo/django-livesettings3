import sys
import types

def can_loop_over(maybe):
    """Test value to see if it is list like"""
    try:
        iter(maybe)
    except:
        return 0
    else:
        return 1

def is_list_or_tuple(maybe):
    return isinstance(maybe, (types.TupleType, types.ListType))


def is_scalar(maybe):
    """Test to see value is a string, an int, or some other scalar type"""
    return is_string_like(maybe) or not can_loop_over(maybe)

def is_string_like(maybe):
    """Test value to see if it acts like a string"""
    try:
        maybe+""
    except TypeError:
        return 0
    else:
        return 1


def flatten_list(sequence, scalarp=is_scalar, result=None):
    """flatten out a list by putting sublist entries in the main list"""
    if result is None:
        result = []

    for item in sequence:
        if scalarp(item):
            result.append(item)
        else:
            flatten_list(item, scalarp, result)

def load_module(module):
    """Load a named python module."""
    try:
        module = sys.modules[module]
    except KeyError:
        __import__(module)
        module = sys.modules[module]
    return module
