from django.test import TestCase
from django.utils import timezone

from datetime import datetime

from currencies.models import Rate, Currency

class APITest(TestCase):
    def setUp(self):
        self.base_currency_code = "USD"
        self.quote_currency_code = "EUR"
        self.base_currency_obj = Currency.objects.create(code=self.base_currency_code)
        self.quote_currency_obj = Currency.objects.create(code=self.quote_currency_code)
        self.obj = Rate.objects.create(base_currency=self.base_currency_obj,
                            quote_currency=self.quote_currency_obj,
                            exchange_rate=1.234,
                            timestamp=timezone.make_aware(datetime(2024, 1, 1, 12, 0, 0)))

    def test_get_currency_list(self):
        """
        Test if list request GET(/currency/) returns proper result.
        """
        response = self.client.get("/api/currency/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertIn('USD', response.json()[0]['code'])

    def test_get_rate_detail(self):
        """
        Test if detail request GET(/currency/.../.../) returns proper result.
        """ 
        response = self.client.get(f"/api/currency/{self.base_currency_code}/{self.quote_currency_code}/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertEqual(response.json()['currency_pair'], self.obj.currency_pair)
        self.assertEqual(response.json()['exchange_rate'], self.obj.exchange_rate)

    def test_get_invalid_rate_detail(self):
        """
        Test if returns blank ({}) for invalid code.
        """
        response = self.client.get(f"/api/currency/{self.base_currency_code}/AAAA/")
        self.assertEqual(response.status_code, 200) # HTTP_200_OK
        self.assertEqual(response.json(), {})
