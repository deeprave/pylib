"""
Ordered dictionary
"""
from .pyver import PY36

_D = object()


if PY36:

    """
    Python 3.6+ supports ordered dictionaries natively so we just overlay some additional functionality:
        - ability to accept multiple dicts as initializers
        - ability to accept (ordered) args containing (key, value) tuples (a list/tuple
          of same is already supported by dict
        - insert and append functions for managing key,value order
        - ensure odict.copy() return an odict without scrambling order
    """

    # noinspection PyPep8Naming
    class odict(dict):

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

        def pop(self, key, default=_D):
            try:
                item = self.__getitem__(key)
                self.__delitem__(key)
                return item
            except (KeyError, IndexError):
                if default is _D:
                    raise
            return default

        def insert(self, key, value, index=None):
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
                new_dict = odict()
                for i, (k, v) in enumerate(self.items()):
                    if i == idx:
                        new_dict[key] = value
                    if k != key:
                        new_dict[k] = v
                self.clear()
                self.update(new_dict)

        @property
        def inverse(self):
            inversion = odict()
            for k, v in self:
                inversion.append(v, k)
            return inversion

        def append(self, key, value):
            dict.__setitem__(self, key, value)

        def copy(self):
            """ normal dict.copy() won't work, need to order the tuples """
            return odict(self.items())

else:

    _D = object()

    # noinspection PyPep8Naming
    class odict(dict):
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
                        if hasattr(arg, '__len__') and len(arg) == 2 and not isinstance(arg[0], (list, tuple, set)):
                            self.__setitem__(*arg)
                        else:
                            for (key, value) in arg:
                                self.__setitem__(key, value)
            for key, value in kwargs.items():
                self.__setitem__(key, value)

        def __contains__(self, key):
            return key in self._keys_

        def __setitem__(self, key, value):
            if key not in self._keys_:
                self._keys_.append(key)
            return dict.__setitem__(self, key, value)

        def __delitem__(self, key):
            self._keys_.remove(key)
            return dict.__delitem__(self, key)

        def insert(self, key, value, index=None):
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
                dict.__setitem__(self, key, value)
                if key in self._keys_:
                    self._keys_.remove(key)
                self._keys_.insert(index, key)

        @property
        def inverse(self):
            inversion = odict()
            for k, v in self.items():
                inversion.append(v, k)
            return inversion

        def append(self, key, value):
            dict.__setitem__(self, key, value)
            if key in self._keys_:
                self._keys_.remove(key)
            self._keys_.append(key)

        def pop(self, key, default=_D):
            try:
                item = self.__getitem__(key)
                self.__delitem__(key)
                return item
            except (KeyError, IndexError):
                if default is _D:
                    raise
            return default

        def clear(self):
            dict.clear(self)
            try:
                # noinspection PyUnresolvedReferences
                self._keys_.clear()     # only in py3
            except AttributeError:
                self._keys_ = []        # so simulate less efficiently in py2

        def keys(self):
            return self._keys_[:]

        iterkeys = keys

        def items(self):
            return [(key, dict.__getitem__(self, key)) for key in self._keys_]

        iteritems = items

        def values(self):
            return [dict.__getitem__(self, key) for key in self._keys_]

        itervalues = values

        def copy(self):
            """ normal dict.copy() won't work, need to order the tuples """
            return odict(self.items())

        def __repr__(self):
            items = ['{}: {}'.format(repr(key), repr(val)) for key, val in self.items()]
            return '{' + ','.join(items) + '}'
