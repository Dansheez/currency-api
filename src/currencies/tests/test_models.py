from django.test import TestCase
from django.utils import timezone

from datetime import datetime, timedelta

from currencies.models import Rate, Currency

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
            self.obj = Rate.objects.create(base_currency=self.base_currency_obj,
                                           quote_currency=self.quote_currency_obj,
                                           exchange_rate=1.234,
                                           time=(self.base_time+timedelta(minutes=i)).time(),
                                           date=self.base_time.date())
        self.latest_obj = Rate.get_latest(base_currency__code=self.base_currency_code,
                                          quote_currency__code=self.quote_currency_code)

    def test_currency_pair_property(self):
        """
        Tests if currency_pair property generates properly. 
        """
        self.assertEqual(self.obj.currency_pair, f"{self.base_currency_code}{self.quote_currency_code}")

    def test_order(self):
        """
        Tests Rate get_latest() method. 
        """
        self.assertEqual(self.obj.time, (self.base_time+timedelta(minutes=self.number_of_obj-1)).time())
        self.assertEqual(self.obj.date, self.base_time.date())

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
        self.assertEqual(self.updated_obj.code, "EUR")
