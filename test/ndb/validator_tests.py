# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import unittest
from google.appengine.ext import ndb
from gaevalidator.base import IntegerField
from gaevalidator.ndb.validator import ModelValidator


class IntegerModelMock(ndb.Model):
    integer = ndb.IntegerProperty()
    integer_required = ndb.IntegerProperty(required=True)
    integer_repeated = ndb.IntegerProperty(repeated=True)
    integer_choices = ndb.IntegerProperty(choices=[1, 2])
    integer_default = ndb.IntegerProperty(default=0)


class IntegerModelValidator(ModelValidator):
    _model_class = IntegerModelMock


class ModelValidatorTests(unittest.TestCase):
    def test_fields(self):
        properties = ['integer', 'integer_required', 'integer_repeated',
                      'integer_choices', 'integer_default']
        self.assertSetEqual(set(properties),set(IntegerModelValidator._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerModelValidator._fields[p], IntegerField)

    def test_include(self):
        properties = ['integer', 'integer_required']

        class IntegerInclude(ModelValidator):
            _model_class = IntegerModelMock
            _include = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertSetEqual(set(properties),set(IntegerInclude._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerInclude._fields[p], IntegerField)

    def test_exclude(self):
        properties = ['integer_repeated','integer_choices', 'integer_default']

        class IntegerInclude(ModelValidator):
            _model_class = IntegerModelMock
            _exclude = (IntegerModelMock.integer, IntegerModelMock.integer_required)

        self.assertSetEqual(set(properties),set(IntegerInclude._fields.iterkeys()))
        for p in properties:
            self.assertIsInstance(IntegerInclude._fields[p], IntegerField)
