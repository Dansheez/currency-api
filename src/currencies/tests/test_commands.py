from django.test import TestCase
from django.core.management import CommandError, call_command

class YFinanceTestCase(TestCase):
    def setUp(self):
        self.command_name = "fetch_data"

    def test_symbol_count(self):
        """
        Test if command with only one symbol fails.
        """
        with self.assertRaises(CommandError):
            call_command(self.command_name, "USD")

    def test_invalid_currency_symbol_argument(self):
        """
        Test if command with symbol with four or two digits fails.
        """
        with self.assertRaises(CommandError):
            call_command(self.command_name, 'USD,AAAA')
        with self.assertRaises(CommandError):
            call_command(self.command_name, "USD,AA")
        # NOTE: maybe test if command runs succesfully with exacty three letters symbols.
        # Need to rearange how command works to not run too many api calls tho.

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
