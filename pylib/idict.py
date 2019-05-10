# -*- coding: utf-8 -*-
"""
Case insensitive dict
Note: only supports text keys
"""
_D = object()


# noinspection PyPep8Naming
class idict(dict):
    """
    dict with order
    simple implementation with the additional overhead is a list of keys

    :param args: dict, list of tuples
    :param kwargs: expanded key=value airs
    """

    def __init__(self, *args, **kwargs):
        # noinspection PyArgumentList
        dict.__init__(self)
        self._keys_ = []
        self.update(*args, **kwargs)

    def update(self, *args, **kwargs):
        for arg in args:
            if arg:
                if isinstance(arg, dict):
                    for key, value in arg.items():
                        self.__setitem__(key, value)
                elif isinstance(arg, (tuple, list, set)) or hasattr(arg, '__iter__'):
                    if len(arg) == 2 and not isinstance(arg[0], (list, tuple, set)):
                        self.__setitem__(*arg)
                    else:
                        for (key, value) in arg:
                            self.__setitem__(key, value)
        for key, value in kwargs.items():
            self.__setitem__(key, value)

    @staticmethod
    def convert(obj):
        # recursive conversion of dict to ordered case insensitive dict
        # note: keys of same name but different case may be silently overwritten

        def _convert(arg):
            if isinstance(arg, dict):
                result = idict()
                for key, val in arg.items():
                    result[key] = _convert(val)
                return result
            elif isinstance(arg, (list, tuple, set)):
                _type = type(arg)
                result = []
                for val in arg:
                    result.append(_convert(val))
                return _type(result)
            return arg

        return _convert(obj)

    def __contains__(self, key):
        lkey = key.lower()
        return lkey in self._keys_

    def __getitem__(self, key):
        lkey = key.lower()
        item = dict.__getitem__(self, lkey)
        return None if item is None else item[1]

    def __setitem__(self, key, value):
        lkey = key.lower()
        if lkey not in self._keys_:
            self._keys_.append(lkey)
        return dict.__setitem__(self, lkey, (key, value))

    def __delitem__(self, key):
        lkey = key.lower()
        self._keys_.remove(lkey)
        return dict.__delitem__(self, lkey)

    def insert(self, key, value, index=None):
        lkey = key.lower()
        idx, length = index, len(self.keys())
        if idx is None:
            idx = length
        elif idx < 0:  # negative wrap to length
            idx += length
        if idx == length:
            self.append(key, value)
        else:
            if idx < 0 or idx > length:
                raise IndexError('at=%d (len=%d)' % (index, length))
            dict.__setitem__(self, lkey, (key, value))
            if lkey in self._keys_:
                self._keys_.remove(lkey)
            self._keys_.insert(index, lkey)

    def append(self, key, value):
        lkey = key.lower()
        dict.__setitem__(self, lkey, (key, value))
        if lkey in self._keys_:
            self._keys_.remove(lkey)
        self._keys_.append(lkey)

    def get(self, key, default=_D):
        try:
            item = self.__getitem__(key)
            return item
        except (KeyError, IndexError):
            pass
        return None if default is _D else default

    def pop(self, key, default=_D):
        try:
            item = self.__getitem__(key)
            self.__delitem__(key)
            return item
        except (KeyError, IndexError):
            if default is _D:
                raise
        return None if default is _D else default

    def clear(self):
        dict.clear(self)
        try:
            # noinspection PyUnresolvedReferences
            self._keys_.clear()     # only in py3
        except AttributeError:
            self._keys_ = []        # so simulate less efficiently in py2

    def keys(self):
        return [dict.__getitem__(self, key)[0] for key in self._keys_]

    iterkeys = keys

    def items(self):
        return [dict.__getitem__(self, key) for key in self._keys_]

    iteritems = items

    def values(self):
        return [self.__getitem__(key) for key in self._keys_]

    itervalues = values

    def copy(self):
        """ normal dict.copy() won't work, need to order the tuples """
        return idict(self.items())

    def __eq__(self, other):
        if isinstance(other, dict):
            if len(other.keys()) == len(self.keys()):
                for key, value in self.items():
                    if other.get(key) != self.get(key):
                        break
                else:
                    return True
        return False

    def __repr__(self):
        items = ['{}: {}'.format(repr(key), repr(val)) for key, val in self.items()]
        return '{' + ','.join(items) + '}'
