import unittest
import json
import redis
import logging
from internal import add_data_point, generate_data_point_id

class InternalTestCase(unittest.TestCase):
    def setUp(self):
        self.redis_conn = redis.Redis(host="redis", port=6379)
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        self.redis_conn.flushall()

    def test_add_data_point_properly_formatted(self):
        data_point = {
            "dataSource": "test",
            "updateFrequency": 60,
            "price": 100
        }
        expected_data_point_id = "eea12de80a09eaae4172d0f8ae0243d2d1629e3abe88ac839e790e22fea12f70"

        result = add_data_point(data_point, self.redis_conn, self.logger)

        self.assertIsNotNone(result)
        self.assertIn("dataPointID", result)
        self.assertEqual(result["dataPointID"], expected_data_point_id)
        stored_data_point = json.loads(self.redis_conn.get(f"data:{expected_data_point_id}"))
        self.assertEqual(stored_data_point["dataSource"], data_point["dataSource"])
        self.assertEqual(stored_data_point["updateFrequency"], data_point["updateFrequency"])
        self.assertEqual(stored_data_point["price"], data_point["price"])

    def test_add_data_point_missing_price_field(self):
        data_point = {
            "dataSource": "test",
            "updateFrequency": 60,
        }

        result = add_data_point(data_point, self.redis_conn, self.logger)

        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid request: Missing 'price' field")
        self.assertIsNone(self.redis_conn.get("data:test"))

    def test_add_data_point_missing_data_source_field(self):
        data_point = {
            "updateFrequency": 60,
            "price": 100
        }

        result = add_data_point(data_point, self.redis_conn, self.logger)

        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid request: Missing 'dataSource' field")
        self.assertIsNone(self.redis_conn.get("data:60"))

    def test_add_data_point_missing_update_frequency_field(self):
        data_point = {
            "dataSource": "test",
            "price": 100
        }

        result = add_data_point(data_point, self.redis_conn, self.logger)

        self.assertIsNotNone(result)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Invalid request: Missing 'updateFrequency' field")
        self.assertIsNone(self.redis_conn.get("data:test"))

    def test_generate_data_point_id(self):
        data_source = "test"
        update_frequency = 60
        expected_id = "eea12de80a09eaae4172d0f8ae0243d2d1629e3abe88ac839e790e22fea12f70"

        data_point_id = generate_data_point_id(data_source, update_frequency)

        self.assertEqual(data_point_id, expected_id)

    def test_generate_data_point_id_different_inputs(self):
        data_source = "other"
        update_frequency = 120
        expected_id = "0e9f125ac86de59a17e17f46983122c22eb72d5a73247e3ecf75a418ba71fb0a"

        data_point_id = generate_data_point_id(data_source, update_frequency)

        self.assertEqual(data_point_id, expected_id)

if __name__ == '__main__':
    unittest.main()
