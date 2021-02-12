from unittest import TestCase
from shipt.api import app

""" Running these tests individually may result in failures, as some tests are dependent on the state of the database,
which is modified by some tests """

class TestCustomerHistory(TestCase):

    def test_customer_history(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/history/1')
            json_data = response.get_json()
            test = {
                "1": [
                    {"datetime": "2020-11-02", "delivered": None, "on its way": None, "order id": "4", "products": {"1": {"tire": 1.0}}, "ready": None},
                    {"datetime": "2020-07-15", "delivered": None, "on its way": None, "order id": "3", "products": {"3": {"oil": 1.0}}, "ready": None},
                    {"datetime": "2020-01-01", "delivered": None, "on its way": None, "order id": "1", "products": {"1": {"tire": 2.0}, "2": {"bike": 1.0}}, "ready": None}
                ]
            }
            self.assertDictEqual(test, json_data)

    def test_customer_history_customer_not_exists(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/history/9')
            json_data = response.get_json()
            test = {"9": "no orders!"}
            self.assertDictEqual(test, json_data)

    def test_customer_history_no_history(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/history/3')
            json_data = response.get_json()
            test = {"3": "no orders!"}
            self.assertDictEqual(test, json_data)

class TestZCustomerPurchase(TestCase):
    """ Runs last due to table insertions in tests, hence the 'Z' in the class name """

    def test_0_customer_purchase_new_customer(self):
        with app.test_client() as api:
            response = api.post('/shipt/api/v1/purchase', json={"customer": "brent", "products": {"2": 1}})
            json_data = response.get_json()
            test = {
                "customer_id": 4,
                "order": 6,
                "purchase": {"2": 1.0}
            }
            self.assertDictEqual(test, json_data)

    def test_1_customer_purchase_existing_customer(self):
        with app.test_client() as api:
            response = api.post('/shipt/api/v1/purchase', json={"customer": 3, "products": {"2": 1}})
            json_data = response.get_json()
            test = {
                "customer_id": 3,
                "order": 7,
                "purchase": {"2": 1.0}
            }
            self.assertDictEqual(test, json_data)

    def test_2_customer_purchase_given_customer_not_exists(self):
        with app.test_client() as api:
            response = api.post('/shipt/api/v1/purchase', json={"customer": 9, "products": {"2": 1}})
            json_data = response.get_json()
            test = {"error": "need valid customer id"}
            self.assertDictEqual(test, json_data)

    def test_3_customer_purchase_product_not_exist(self):
        with app.test_client() as api:
            response = api.post('/shipt/api/v1/purchase', json={"customer": 3, "products": {"50": 1}})
            json_data = response.get_json()
            test = {"error": "need valid products and volumes"}
            self.assertDictEqual(test, json_data)

    def test_customer_purchase_bad_weight(self):
        with app.test_client() as api:
            response = api.post('/shipt/api/v1/purchase', json={"customer": 3, "products": {"2": "hhh"}})
            json_data = response.get_json()
            test = {"error": "need valid products and volumes"}
            self.assertDictEqual(test, json_data)

class TestSalesData(TestCase):

    def test_sales_data_bad_unit(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/data/20200101/20201125/bad')
            json_data = response.get_json()
            test = {
                "error": "/shipt/api/v1/data/<starting:yyyymmdd>/<ending:yyyymmdd>/<unit:['day','week','month']>"
            }
            self.assertDictEqual(test, json_data)

    def test_sales_data_week(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/data/20200101/20201225/week')
            json_data = response.get_json()
            test = {
                "week": {
                    "00-2020": [
                        {"name": "tire", "product id": 1, "volume": 2.0},
                        {"name": "bike", "product id": 2, "volume": 1.0},
                        {"name": "oil", "product id": 3, "volume": 1.0}
                    ],
                    "28-2020": [
                        {"name": "oil", "product id": 3, "volume": 1.0}
                    ],
                    "44-2020": [
                        {"name": "tire", "product id": 1, "volume": 2.0}
                    ]
                }
            }
            self.assertDictEqual(test, json_data)

    def test_sales_data_day(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/data/20200101/20201125/day')
            json_data = response.get_json()
            test = {
                "day": {
                    "001-2020": [
                        {"name": "tire", "product id": 1, "volume": 2.0},
                        {"name": "bike", "product id": 2, "volume": 1.0}
                    ],
                    "003-2020": [
                        {"name": "oil", "product id": 3, "volume": 1.0}
                    ],
                    "197-2020": [
                        {"name": "oil", "product id": 3, "volume": 1.0}
                    ],
                    "307-2020": [
                        {"name": "tire", "product id": 1, "volume": 1.0}
                    ],
                    "308-2020": [
                        {"name": "tire", "product id": 1, "volume": 1.0}
                    ]
                }
            }
            self.assertDictEqual(test, json_data)

    def test_sales_data_month(self):
        with app.test_client() as api:
            response = api.get('/shipt/api/v1/data/20200101/20201225/month')
            json_data = response.get_json()
            test = {
                "month": {
                    "01-2020": [
                        {"name": "tire", "product id": 1, "volume": 2.0},
                        {"name": "bike", "product id": 2, "volume": 1.0},
                        {"name": "oil", "product id": 3, "volume": 1.0}
                    ],
                    "07-2020": [
                        {"name": "oil", "product id": 3, "volume": 1.0}
                    ],
                    "11-2020": [
                        {"name": "tire", "product id": 1, "volume": 2.0}
                    ]
                }
            }
            self.assertDictEqual(test, json_data)

