# -*- coding: utf-8 -*-
from typing import List, Union


class openbuf:
    """quick and dirty context manager to capture result or output to file"""

    def __init__(self, filename, flags, result=None, with_trim=True):
        """
        :param filename: filename to access
        :param flags: open flags
        :param result: a list object to which results are added
        """
        # type: (str, str, Union[List,None], bool)
        self.filename = filename
        self.flags = flags
        self.result = result
        self.with_trim = with_trim

    def __enter__(self):
        from .bufferio import BufferIO
        self.fp = open(self.filename, self.flags) if self.filename else BufferIO()
        return self.fp

    def __exit__(self, exc_type, exc_value, traceback):
        if self.fp:
            if self.result is not None:
                if self.filename:
                    self.result.append(self.filename)
                else:
                    lines = self.fp.getvalue().split("\r\n")
                    if self.with_trim:
                        for i in range(len(lines), 0, -1):
                            idx = i - 1     # remove non-content lines at end
                            if lines[idx].count(',') + lines[idx].count('\'') + \
                               lines[idx].count('"') == len(lines[idx]):
                                del lines[idx]
                            else:
                                break
                    self.result.append(lines)
            self.fp.close()
