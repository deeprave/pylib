# -*- coding: utf-8 -*-


def cleaner(element, accept, level=0, key_only=False):
    """
    Clean a structure (list or dict based) based on cleanfunc()
    :param element: element to clean
    :param accept: function to call to determine acceptance
    :param level: recursion level
    :return: cleaned element
    """

    if isinstance(element, dict):
        # handle a dictionary
        result = dict()
        for k, v in element.items():
            if accept(k) and (key_only or accept(v)):
                # recurse to clean elements
                res = cleaner(v, accept, level + 1, key_only=key_only)
                # if none is returned, don't propogate
                if res is not None:
                    result[k] = res
        return result

    if isinstance(element, (list, tuple, set)):
        # handle a list
        result = []
        for item in element:
            res = cleaner(item, accept, level + 1, key_only=key_only)
            if res is not None:
                result.append(res)
        return set(result) if isinstance(element, set) else tuple(result) if isinstance(element, tuple) else result

    return element if key_only or accept(element) else None
