# -*- coding: utf-8 -*-
from .pyver import PY2

__all__ = (
    'BufferIO',
    'StringIO',
)


if PY2:
    from io import BytesIO, StringIO

    class BufferIO(BytesIO):
        pass

else:
    from io import StringIO

    class BufferIO(StringIO):
        pass
