# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from decimal import Decimal
import unittest
import datetime
from gaevalidator.base import BaseField, Validator, IntegerField, DecimalField, StringField, DateField


def error_msg(attr_name):
    return '%s has error' % attr_name


class MockField(BaseField):
    def validate_field(self, value):
        if not value:
            return error_msg(self._attr)

    def transform_field(self, value):
        return int(value)


mock1 = MockField()
mock2 = MockField()


class ValidatorExample(Validator):
    attr1 = mock1
    attr2 = mock2
    non_field = 'foo'


class ValidatorTests(unittest.TestCase):
    def test_fields(self):
        self.assertDictEqual({'attr1': mock1, 'attr2': mock2}, ValidatorExample._fields)

    def test_instance_values(self):
        v1 = ValidatorExample(attr1='a', attr2='b')
        v2 = ValidatorExample(attr1='c', attr2='d')
        self.assertTupleEqual(('a', 'b'), (v1.attr1, v1.attr2))
        self.assertTupleEqual(('c', 'd'), (v2.attr1, v2.attr2))


    def test_validate(self):
        v1 = ValidatorExample(attr1=True, attr2=True)
        self.assertDictEqual({}, v1.validate())
        v1 = ValidatorExample(attr1=False, attr2=True)
        self.assertDictEqual({'attr1': error_msg('attr1')}, v1.validate())
        v1 = ValidatorExample(attr1=True, attr2=False)
        self.assertDictEqual({'attr2': error_msg('attr2')}, v1.validate())
        v1 = ValidatorExample(attr1=False, attr2=False)
        self.assertDictEqual({'attr1': error_msg('attr1'), 'attr2': error_msg('attr2')}, v1.validate())

    def test_transform(self):
        v1 = ValidatorExample(attr1='1', attr2='2')
        self.assertDictEqual({'attr1': 1, 'attr2': 2}, v1.transform())


class BaseFieldTests(unittest.TestCase):
    def test_required(self):
        field_not_required = BaseField()
        self.assertIsNone(None, field_not_required.validate(''))
        self.assertIsNone(field_not_required.validate(None))
        self.assertIsNone(field_not_required.validate('Foo'))
        field_required = BaseField(required=True)
        self.assertIsNotNone(field_required.validate(''))
        self.assertIsNotNone(field_required.validate(None))
        self.assertIsNone(field_required.validate('Foo'))

    def test_default(self):
        DEFAULT = 'default'
        field = BaseField(default=DEFAULT)
        self.assertEqual(DEFAULT, field.transform(''))
        self.assertEqual(DEFAULT, field.transform(None))
        self.assertEqual("X", field.transform('X'))

    def test_default_plus_required(self):
        DEFAULT = 'default'
        field = BaseField(default=DEFAULT, required=True)
        self.assertEqual(DEFAULT, field.transform(''))
        self.assertEqual(DEFAULT, field.transform(None))
        self.assertEqual("X", field.transform('X'))
        self.assertIsNone(None, field.validate(''))
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate('X'))

    def test_choices(self):
        field = BaseField(choices=['1', '2'])
        self.assertIsNone(field.validate('1'))
        self.assertIsNone(field.validate('2'))
        self.assertIsNotNone(field.validate(None))

    def test_repeated(self):
        field = BaseField(repeated=True)
        self.assertIsNone(field.validate([]))
        self.assertIsNone(field.validate(['1']))
        self.assertIsNone(field.validate(['1', '2']))
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate([None]))

    def test_repeated_plus_required(self):
        field = BaseField(repeated=True, required=True)
        self.assertIsNone(field.validate(['1']))
        self.assertIsNone(field.validate(['1', '2']))
        self.assertIsNotNone(field.validate(None))
        self.assertIsNotNone(field.validate([None]))
        self.assertIsNotNone(field.validate([]))
        self.assertIsNotNone(field.validate(['1,', None]))

    def test_repeated_transformation(self):
        field = MockField(repeated=True)
        self.assertListEqual([1, 2, 3], field.transform(['1', '2', '3']))


class IntergerFieldTests(unittest.TestCase):
    def test_transformation(self):
        field = IntegerField()
        self.assertIsNone(field.transform(None))
        self.assertIsNone(field.transform(''))
        self.assertEqual(0, field.transform(0))
        self.assertEqual(1, field.transform(1))
        self.assertEqual(0, field.transform('0'))
        self.assertEqual(1, field.transform('1'))

    def test_validation(self):
        field = IntegerField()
        field._set_attr_name('n')
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate(0))
        self.assertIsNone(field.validate(1))
        self.assertIsNone(field.validate('0'))
        self.assertIsNone(field.validate('1'))
        self.assertEqual('n must be integer', field.validate('foo'))
        self.assertEqual('n must be integer', field.validate('123h'))
        self.assertEqual('n must be integer', field.validate('0x456'))

    def test_validation_lower(self):
        field = IntegerField(lower=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('n must be greater than 1', field.validate('0'))

    def test_validation_upper(self):
        field = IntegerField(upper=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('n must be less than 1', field.validate('2'))


class SimpleDecimalFieldTests(unittest.TestCase):
    def test_transformation(self):
        field = DecimalField()
        self.assertIsNone(field.transform(None))
        self.assertIsNone(field.transform(''))
        self.assertEqual(Decimal('0.00'), field.transform(0))
        self.assertEqual(Decimal('1.34'), field.transform(1.339999999))
        self.assertEqual(Decimal('0.00'), field.transform('0'))
        self.assertEqual(Decimal('1.34'), field.transform('1.34'))
        field = DecimalField(decimal_places=3)
        self.assertEqual(Decimal('1.340'), field.transform(1.339999999))

    def test_validation(self):
        field = DecimalField()
        field._set_attr_name('n')
        self.assertIsNone(field.validate(None))
        self.assertIsNone(field.validate(''))
        self.assertIsNone(field.validate(0))
        self.assertIsNone(field.validate(1))
        self.assertIsNone(field.validate('0'))
        self.assertIsNone(field.validate('1'))
        self.assertEqual('n must be a number', field.validate('foo'))
        self.assertEqual('n must be a number', field.validate('123h'))
        self.assertEqual('n must be a number', field.validate('0x456'))

    def test_validation_lower(self):
        field = DecimalField(lower=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('n must be greater than 1', field.validate('0'))

    def test_validation_upper(self):
        field = DecimalField(upper=1)
        field._set_attr_name('n')
        self.assertIsNone(field.validate('1'))
        self.assertEqual('n must be less than 1', field.validate('2'))


class StringFieldTests(unittest.TestCase):
    def test_str_with_more_than_500_chars(self):
        field = StringField()
        field._set_attr_name('n')
        self.assertEqual('n has 501 characters and it must have less than 500', field.validate_field('a' * 501))


class DateFieldTests(unittest.TestCase):
    def test_default_transformation(self):
        field = DateField()
        field._set_attr_name('d')
        dt = field.transform('2000/09/30')
        self.assertEqual(datetime.datetime(2000, 9, 30), dt)

    def test_transformation(self):
        field = DateField(r'%Y/%m/%d %H:%M:%S')
        field._set_attr_name('d')
        dt = field.transform('2000/09/30 23:59:59')
        self.assertEqual(datetime.datetime(2000, 9, 30, 23, 59, 59), dt)

    def test_validate(self):
        field = DateField(r'%Y/%m/%d %H:%M:%S')
        field._set_attr_name('d')
        self.assertIsNone(field.validate('2000/09/30 23:59:59'))
        self.assertEqual('d must be a date', field.validate('2000/09/30 23:59:a'))

    def test_date_assignment(self):
        field = DateField()
        field._set_attr_name('d')
        date = datetime.datetime(2000, 9, 30)
        dt = field.transform(date)
        self.assertEqual(date, dt)
