from sqlalchemy import Column, Text
import json
import risclog.sqlalchemy.model
import risclog.sqlalchemy.serializer
import unittest
import datetime
import pytz
import decimal


class TestModel(risclog.sqlalchemy.model.Object):
    foo = Column(Text, primary_key=True)

test_object = TestModel()
test_object.foo = u'bar'


class EncoderTest(unittest.TestCase):

    def test_returns_json_serializable_data_of_sqlalchemy_object(self):
        result = risclog.sqlalchemy.serializer.sqlalchemy_encode(test_object)
        self.assertEqual({'foo': u'bar'}, result)

    def test_returns_json_serializable_data_of_date_object(self):
        result = risclog.sqlalchemy.serializer.datetime_encode(
            datetime.date(2013, 6, 20))
        self.assertEqual('2013-06-20', result)

    def test_returns_json_serializable_data_of_decimal_object(self):
        result = risclog.sqlalchemy.serializer.decimal_encode(
            decimal.Decimal('3500.17'))
        self.assertEqual('3500.17', result)


class JSONDumpsMonkeyPatchTest(unittest.TestCase):

    def callFUT(self, data):
        result = json.dumps(data)
        return json.loads(result)

    def test_json_dumps_can_dump_sqlalchemy_objects(self):
        self.assertEqual([{'foo': u'bar'}, {'foo': u'bar'}],
                         self.callFUT([test_object, test_object]))

    def test_json_dumps_can_dump_dates_and_datetimes(self):
        self.assertEqual(
            [u'2013-06-20', u'2013-06-20T09:55:12'],
            self.callFUT([datetime.date(2013, 6, 20),
                          datetime.datetime(2013, 6, 20, 9, 55, 12)]))
        self.assertEqual(
            u'2013-06-20T09:55:12+00:00',
            self.callFUT(
                datetime.datetime(2013, 6, 20, 9, 55, 12, tzinfo=pytz.utc)))

    def test_json_dumps_can_dump_decimals(self):
        self.assertEqual(
            u'12345.67', self.callFUT(decimal.Decimal('12345.67')))