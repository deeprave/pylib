# -*- coding: utf-8 -*-
"""
support for strict order for json read/write for ordered directs
"""
import json

__all__ = (
    'OrderedJSONEncoder'
)


class OrderedJSONEncoder(json.JSONEncoder):
    ordered = True

    def encode(self, o):
        # this is basically a hack, we want to void the c encoder as it
        # shuffles dict keys regardless of being passed an ordered dict
        c_make_encoder = json.encoder.c_make_encoder = None
        try:
            return super(OrderedJSONEncoder, self).encode(o)
        finally:
            json.encoder.c_make_encoder = c_make_encoder

