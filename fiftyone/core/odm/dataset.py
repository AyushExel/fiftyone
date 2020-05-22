"""
FiftyOne meta-datasets.

Defines an :class:`ODMDataset` class that represents a "meta dataset" database
collection used to keep track of all persistent datasets.

| Copyright 2017-2020, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""
# pragma pylint: disable=redefined-builtin
# pragma pylint: disable=unused-wildcard-import
# pragma pylint: disable=wildcard-import
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import *
from future.utils import itervalues

# pragma pylint: enable=redefined-builtin
# pragma pylint: enable=unused-wildcard-import
# pragma pylint: enable=wildcard-import

from mongoengine import (
    StringField,
    EmbeddedDocumentListField,
)

import eta.core.utils as etau

from .document import ODMDocument, ODMEmbeddedDocument


class SampleField(ODMEmbeddedDocument):
    """Backing document for sample fields."""

    name = StringField()
    ftype = StringField()
    subfield = StringField(null=True)
    embedded_doc_type = StringField(null=True)

    @classmethod
    def from_field(cls, field):
        """Creates a :class:`SampleField` from a MongoEngine field.

        Args:
            field: a ``mongoengine.fields.BaseField`` instance

        Returns:
            a :class:`SampleField`
        """
        return cls(
            name=field.name,
            ftype=etau.get_class_name(field),
            subfield=cls._get_class_name(field, "field"),
            embedded_doc_type=cls._get_class_name(field, "document_type"),
        )

    @classmethod
    def list_from_field_schema(cls, d):
        """Creates a list of :class:`SampleField` objects from a field schema.

        Args:
             d: a dict generated by
                :func:`fiftyone.core.dataset.Dataset.get_sample_fields` or
                :func:`fiftyone.core.sample.Sample.get_field_schema`

        Returns:
             a list of :class:`SampleField` objects
        """
        return [
            cls.from_field(field)
            for field in itervalues(d)
            if field.name != "id"
        ]

    def matches_field(self, field):
        """Determines whether this sample field matches the given field.

        Args:
            field: a ``mongoengine.fields.BaseField`` instance

        Returns:
            True/False
        """
        if self.name != field.name:
            return False

        if self.ftype != etau.get_class_name(field):
            return False

        if self.subfield and self.subfield != etau.get_class_name(field.field):
            return False

        if (
            self.embedded_doc_type
            and self.embedded_doc_type
            != etau.get_class_name(field.document_type)
        ):
            return False

        return True

    @staticmethod
    def _get_class_name(field, attr_name):
        attr = getattr(field, attr_name, None)
        return etau.get_class_name(attr) if attr else None


class ODMDataset(ODMDocument):
    """Meta-collection that tracks and persists datasets."""

    name = StringField(unique=True)
    sample_fields = EmbeddedDocumentListField(document_type=SampleField)
