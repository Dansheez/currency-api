from django.test import TestCase
from django.core.management import CommandError, call_command

from currencies.management.commands.fetch_data import generate_yfinance_tickers
from currencies.models import Currency, Rate

class YFinanceTestCase(TestCase):
    def setUp(self):
        self.command_name = "fetch_data"

    def test_passing_one_currency_symbol_argument(self):
        """
        Test if command with only one symbol fails.
        """
        with self.assertRaises(CommandError):
            call_command(self.command_name, "USD")

    def test_digit_check_currency_symbol_argument(self):
        """
        Test if command with symbol with four or two digits fails.
        """
        with self.assertRaises(CommandError):
            call_command(self.command_name, 'USD,AAAA')
        with self.assertRaises(CommandError):
            call_command(self.command_name, "USD,AA")

    def test_invalid_period_argument(self):
        """
        Test if command catches invalid argument of period argument.
        valid_periods = ["1d", "5d", "1mo", "3mo" "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] 
        """
        with self.assertRaises(CommandError):
            call_command(self.command_name, "USD,EUR", period="bbb")

    def test_invalid_interval_argument(self):
        """
        Test if command catches invalid argument of interval argument.
        valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
        """
        with self.assertRaises(CommandError):
            call_command(self.command_name, "USD,EUR", interval="bbb")

    def test_command_expected_result(self):
        """
        Test if command overall result (number of created model instances) because reading multi-level-index csv file from yfinance is a little nightmare. 
        """
        self.sample_symbols = "EUR,USD,PLN"
        self.sample_symbol_list = self.sample_symbols.split(",")
        call_command(self.command_name, self.sample_symbols, start="2024-11-22", end="2024-11-24") # 1 row for each ticker
        currency_count = Currency.objects.count()
        self.assertEqual(currency_count, len(self.sample_symbol_list))
        expected_rate_count = len(generate_yfinance_tickers(self.sample_symbol_list, False))
        rate_count = Rate.objects.count()
        self.assertEqual(rate_count, expected_rate_count)

