# -*- coding: utf-8 -*-
"""
A dict that implements MutableAttr.
"""
from .attr import mutable_attr

__all__ = (
    'attrdict',
)


# noinspection PyPep8Naming
class attrdict(dict, mutable_attr):
    """
    A dict that implements MutableAttr.
    """

    def __init__(self, *args, **kwargs):
        super(attrdict, self).__init__(*args, **kwargs)
        self._setattr('_sequence_type', tuple)
        self._setattr('_allow_invalid_attributes', False)

    def _configuration(self):
        """
        The configuration for an attrdict instance.
        """
        return self._sequence_type

    def __getstate__(self):
        """
        Serialize the object.
        """
        return self.copy(), self._sequence_type, self._allow_invalid_attributes

    def __setstate__(self, state):
        """
        Deserialize the object.
        """
        mapping, sequence_type, allow_invalid_attributes = state
        self.update(mapping)
        self._setattr('_sequence_type', sequence_type)
        self._setattr('_allow_invalid_attributes', allow_invalid_attributes)

    def __repr__(self):
        return 'attrdict({})'.format(super(attrdict, self).__repr__())

    def __str__(self):
        return super(attrdict, self).__repr__()

    @classmethod
    def _constructor(cls, mapping, configuration):
        """
        A standardized constructor.
        """
        attr = cls(mapping)
        attr._setattr('_sequence_type', configuration)
        return attr
