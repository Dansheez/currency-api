from django.test import TestCase

from datetime import datetime, timedelta

from .models import Rate, Currency

# Create your tests here.
class RateTestCase(TestCase):
    def setUp(self):
        self.base_currency_code = "USD"
        self.quote_currency_code = "EUR"
        self.base_currency_obj = Currency.objects.create(code=self.base_currency_code)
        self.quote_currency_obj = Currency.objects.create(code=self.quote_currency_code)
        self.base_time = datetime(2024, 1, 1, 12, 0, 0)
        self.number_of_obj = 10
        for i in range(0, self.number_of_obj):
            Rate.objects.create(base_currency=self.base_currency_obj.id,
                                quote_currency=self.quote_currency_obj.id,
                                exchange_rate=1.234,
                                timestamp=self.base_time+timedelta(minutes=i)) 
        self.obj = Rate.objects.filter(base_currency=self.base_currency_obj.id, quote_currency=self.quote_currency_obj.id).first()

    def test_currency_pair_property(self):
        """
        Tests if currency_pair property generates properly. 
        """
        self.assertEqual(self.obj.currency_pair, f"{self.base_currency_code}{self.quote_currency_code}")

    def test_order(self):
        """
        Tests if the first returned item is the most recent one.
        """
        self.assertEqual(self.obj.timestamp, self.base_time+timedelta(minutes=self.number_of_obj-1))

class CurrencyTestCase(TestCase):
    def setUp(self):
        self.obj = Currency.objects.create(code="pln")

    def test_currency_str_representation(self):
        """
        Tests if model uses "code" field when called as a string.
        Also tests uppercase for "code" when creating a model instance.
        """
        self.assertEqual(str(self.obj), "PLN")

    def test_currency_uppercase_update(self):
        """
        Tests if model uppercase code when updating.
        """
        Currency.objects.filter(id=self.obj.id).update(code="eur")
        self.updated_obj = Currency.objects.get(id=self.obj.id) 
        self.assertEqual(self.currency_obj.code, "EUR")

# class YFinanceTestCase(TestCase):
#     def setUp(self):
#         # NOTE: check if custom command creates exact amount of models and check their values
#         # also check if it omits invalid symbols
#         # also maybe check valid periods and intervals??:
#         pass

class APITest(TestCase):
    def setUp(self):
        self.base_currency_code = "USD"
        self.quote_currency_code = "EUR"
        self.base_currency_obj = Currency.objects.create(code=self.base_currency_code)
        self.quote_currency_obj = Currency.objects.create(code=self.quote_currency_code)
        self.base_time = datetime(2024, 1, 1, 12, 0, 0)
        self.obj = Rate.objects.create(base_currency=self.base_currency_obj.id,
                            quote_currency=self.quote_currency_obj.id,
                            exchange_rate=1.234,
                            timestamp=self.basetime+timedelta(minutes=i)) 

    def test_get_currency_list(self):
        response = self.client.get("/api/currencies/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn('USD', response.json()[0]['code'])

    def test_get_rate_detail(self):
        response = self.client.get(f"/currency/{self.base_currency_code}/{self.quote_currency_code}")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn(response.json, self.obj.currency_pair)
        self.assertIn(response.json, self.obj.exchange_rate)
class APITest(TestCase):
    def setUp(self):
        self.base_currency_code = "USD"
        self.quote_currency_code = "EUR"
        self.base_currency_obj = Currency.objects.create(code=self.base_currency_code)
        self.quote_currency_obj = Currency.objects.create(code=self.quote_currency_code)
        self.base_time = datetime(2024, 1, 1, 12, 0, 0)
        self.obj = Rate.objects.create(base_currency=self.base_currency_obj.id,
                            quote_currency=self.quote_currency_obj.id,
                            exchange_rate=1.234,
                            timestamp=self.basetime+timedelta(minutes=i)) 

    def test_get_currency_list(self):
        response = self.client.get("/api/currencies/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn('USD', response.json()[0]['code'])

    def test_get_rate_detail(self):
        response = self.client.get(f"/currency/{self.base_currency_code}/{self.quote_currency_code}")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn(response.json, self.obj.currency_pair)
        self.assertIn(response.json, self.obj.exchange_rate)
class APITest(TestCase):
    def setUp(self):
        self.base_currency_code = "USD"
        self.quote_currency_code = "EUR"
        self.base_currency_obj = Currency.objects.create(code=self.base_currency_code)
        self.quote_currency_obj = Currency.objects.create(code=self.quote_currency_code)
        self.base_time = datetime(2024, 1, 1, 12, 0, 0)
        self.obj = Rate.objects.create(base_currency=self.base_currency_obj.id,
                            quote_currency=self.quote_currency_obj.id,
                            exchange_rate=1.234,
                            timestamp=self.basetime+timedelta(minutes=i)) 

    def test_get_currency_list(self):
        response = self.client.get("/api/currencies/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn('USD', response.json()[0]['code'])

    def test_get_rate_detail(self):
        response = self.client.get(f"/currency/{self.base_currency_code}/{self.quote_currency_code}")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn(response.json, self.obj.currency_pair)
        self.assertIn(response.json, self.obj.exchange_rate)
class APITest(TestCase):
    def setUp(self):
        self.base_currency_code = "USD"
        self.quote_currency_code = "EUR"
        self.base_currency_obj = Currency.objects.create(code=self.base_currency_code)
        self.quote_currency_obj = Currency.objects.create(code=self.quote_currency_code)
        self.base_time = datetime(2024, 1, 1, 12, 0, 0)
        self.obj = Rate.objects.create(base_currency=self.base_currency_obj.id,
                            quote_currency=self.quote_currency_obj.id,
                            exchange_rate=1.234,
                            timestamp=self.basetime+timedelta(minutes=i)) 

    def test_get_currency_list(self):
        response = self.client.get("/api/currencies/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn('USD', response.json()[0]['code'])

    def test_get_rate_detail(self):
        response = self.client.get(f"/currency/{self.base_currency_code}/{self.quote_currency_code}")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn(response.json, self.obj.currency_pair)
        self.assertIn(response.json, self.obj.exchange_rate)

