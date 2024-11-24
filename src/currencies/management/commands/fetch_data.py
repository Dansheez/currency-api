from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from itertools import permutations, product
from datetime import datetime
from typing import List, Dict, Tuple, Set
import pandas as pd
import yfinance as yf

from currencies.models import Currency, Rate

valid_periods = ["1d", "5d", "1mo", "3mo" "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
default_period = "max"
valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]
default_interval = "1d"

class Command(BaseCommand):
    help = "Populate database with a data from yfinance API."

    def add_arguments(self, parser):
        # positional arguments
        parser.add_argument("currency_symbols", type=str,
                            help="""Currencies to load. Separated by comas without spaces.
                            Example: EUR,USD,PLN,JPY""")
        # named (optional) arguments
        parser.add_argument("-p", "--period", type=str,
                            help=f"""Time period to download.
                            Valid periods: {valid_periods}.
                            Default is {default_period}
                            Either use period parameter or use start and end.
                            """)
        parser.add_argument("-i", "--interval", type=str,
                            help=f"""Interval between data points.
                            Valid intervals: {valid_intervals}.
                            Default is {default_interval}.
                            """)
        parser.add_argument("-s", "--start", type=str,
                            help="""Download start date string (YYYY-MM-DD) or _datetime, exclusive.
                            Default is 99 years ago.
                            E.g. for start="2020-01-01", the first data point will be on "2020-01-01".
                            """)
        parser.add_argument("-e", "--end", type=str,
                            help="""Download end date string (YYYY-MM-DD) or _datetime, exclusive.
                            Default is now.
                            E.g. for end="2023-01-01", the last data point will be on "2022-12-31".
                            """)
        parser.add_argument("--selfexchange", action="store_true",
                            help="Include exchange from each currency to itself.")
        parser.add_argument("--conflicts", action="store_true",
                            help="Delete already present coflicting rows in the database and replace them with new values.")
        parser.add_argument("--verbose", action="store_true",
                            help="Show each skipped value.")

    def handle(self, *args, **options):
        # collect arguments
        __self_exchange = options.get("selfexchange")
        __update_conflicts = options.get("conflicts")
        __verbose = options.get("verbose")
        _currency_symbol_list = options["currency_symbols"].split(",")
        _currency_symbol_list = verify_currency_symbol_argument(_currency_symbol_list, __self_exchange)
        _start, _end = verify_date_arguments(options["start"], options["end"])
        _period = verify_period_argument(options["period"])
        if (_period is None) and (_start is None) and (_end is None):
            _period = default_period
        _interval = verify_interval_argument(options["interval"])

        # setup
        exchange_tickers = generate_yfinance_tickers(_currency_symbol_list, __self_exchange)
        # api request
        response = get_data_from_yfinance(exchange_tickers, period=_period, interval=_interval, start=_start, end=_end)
        # process
        model_instances = parse_response_from_yfinance(self, response, exchange_tickers, __update_conflicts, __verbose)
        # create
        self.stdout.write(self.style.SUCCESS(f"\nCreating {len(model_instances)} instances of Rate model."))
        Rate.objects.bulk_create(model_instances)
        self.stdout.write(self.style.SUCCESS(f"\nSuccesfully populated the database."))




def verify_currency_symbol_argument(currency_symbol_list, self_exchange):
    if (not self_exchange) and (len(currency_symbol_list) < 2):
        raise CommandError(f"Not enough currency symbols passed without self exchange flag (need at least two)")
    for symbol in currency_symbol_list:
        if len(symbol) != 3:
            raise CommandError(f"Received invalid currecny symbol '{symbol}'. Make sure all symbols you pass are exactly three characters long and separated by a coma (,).")
    return currency_symbol_list

def verify_period_argument(period):
    if period:
        if period not in valid_periods:
            raise CommandError(f"Received invalid period argument of {period}.\nValid peiods are: {valid_periods}.")
    return period

def verify_interval_argument(interval):
    if interval:
        if interval not in valid_intervals:
            raise CommandError(f"Received invalid interval argument of {interval}.\nValid intervals are: {valid_intervals}.")
    return default_interval

def verify_date_arguments(start, end):
    if (start is not None) and (end is not None):
        try:
            start_datetime = datetime.strptime(start, "%Y-%m-%d")
            end_datetime = datetime.strptime(end, "%Y-%m-%d")
            if end_datetime <= start_datetime:
                raise CommandError(f"Received invalid start or end date argument. Make sure end is later date than start.")
        except ValueError:
            raise CommandError(f"Received invalid start or end date argument. Make sure you pass both arguments as 'YYYY-MM-DD' formatted strings.")
    return (start, end)


def get_existing_currencies_dict():
    """In format of: {"EUR": <Currency: EUR>, "USD": <Currency: USD>, ...}"""
    qs = Currency.objects.all()
    return {obj.code: obj for obj in qs}


def generate_yfinance_tickers(currency_symbol_list: List, self_exchange: bool):
    """
    Generates ticker labels for every possible permutation of passed list elements.
    If "self_exchange" flag is set we include exchange to the same currency (i.e.: EURO to EURO).
    Ticker label format is "<base><quote>=X" (i.e.: "EURUSD=X" for exchanging EURO to US Dollar).
    Parameters:
        currency_symbol_list (list): in format of ["EUR", "USD", ...]
    Returns:
        exchange_tickers (list): in format of ["EURUSD=X", "USDEUR=X", ...]
    """
    if self_exchange:
        currency_pairs = product(currency_symbol_list, repeat=2)
    else:
        currency_pairs = permutations(currency_symbol_list, r=2)
    exchange_tickers = []
    for currency_pair in currency_pairs:
        exchange_tickers.append(f"{currency_pair[0]}{currency_pair[1]}=X")
    return exchange_tickers


def get_data_from_yfinance(exchange_tickers: List, period, interval, start, end):
    return yf.download(exchange_tickers, period=period, interval=interval, start=start, end=end, group_by="ticker", repair=True, keepna=True, multi_level_index=False)


def parse_response_from_yfinance(self, response: pd.DataFrame, exchange_tickers: List, update_conflicts: bool, verbose: bool):
    """
    Fishes out relevant informations from response dataframe and creates a list of models for bulk creation.
    Parameters:
        response (pd.DataFrame): dataframe response from yf.download() method
        exchange_tickers (list): list of tickers in format of ["EURUSD=X", "USDEUR=X", ...]
    Returns:
        model_instances (list): list for bulk creation of models
    """ 
    existing_currencies_dict = get_existing_currencies_dict()
    df = response
    model_instances = []
    skipped = 0
    # (optional) create sets to delete
    created_base_currencies = set()
    created_quote_currencies = set()
    created_timestamps = set()
    for exchange_ticker in exchange_tickers:
        ticker_df = df[exchange_ticker][["Open", "Close"]]
        base_currency_symbol = exchange_ticker[:3]
        quote_currency_symbol = exchange_ticker[3:6]
        for timestamp, row in ticker_df.iterrows():
            ret, _exchange_rate_ = check_rate_for_NaN_values(row)
            if not ret:
                if verbose:
                    self.stdout.write(f"No rate value found for ticker {exchange_ticker} at {timestamp}. Skipping...")
                skipped+=1
                continue
            _base_currency_obj_, existing_currencies_dict = get_currency_obj(self, base_currency_symbol, existing_currencies_dict)
            _quote_currency_obj_, existing_currencies_dict = get_currency_obj(self, quote_currency_symbol, existing_currencies_dict)
            _timestamp_ = timezone.make_aware(timestamp.to_pydatetime())
            model_instances.append(Rate(timestamp=_timestamp_,
                                        base_currency=_base_currency_obj_,
                                        quote_currency=_quote_currency_obj_,
                                        exchange_rate=_exchange_rate_))

            # (optional) add values to delete
            created_base_currencies.add(_base_currency_obj_)
            created_quote_currencies.add(_quote_currency_obj_)
            created_timestamps.add(timestamp)

    # (optional) delete values to update
    if update_conflicts:
        remove_conflicting_values(self, created_timestamps, created_quote_currencies, created_quote_currencies)
    if skipped:
        self.stdout.write(self.style.WARNING(f"Skipped {skipped} rows containing NaN values."))
    return model_instances


def get_currency_obj(self, searched_currency: str, existing_currencies_dict: Dict) -> Tuple[Currency, List]:
    """
    Checks if currency symbol is found in passed currencies dictionary argument.
    If such symbol is not found creates one, updates currency dictionary and returns both object instance and updated list.
    Parameters:
        searched_currency (str): symbol in format of "EUR", "USD", ...
        existing_currencies_dict (dict): dictionary of currently existing currencies in format of {"EUR": <Currency: EUR>, "USD": <Currency: USD>, ...} 
    Returns:
       found_obj (Currency): found or created object instance
       currency_list (list): updated currency dictionary
    """
    try:
        found_obj = existing_currencies_dict[searched_currency]
    except KeyError:
        self.stdout.write(self.style.WARNING(f"Currency {searched_currency} not found in the database. Creating a new instance..."))
        found_obj = Currency.objects.create(code=searched_currency.upper())
        existing_currencies_dict[searched_currency] = found_obj
    return (found_obj, existing_currencies_dict)


def check_rate_for_NaN_values(row):
    if not pd.isna(row["Close"]):
        return True, row["Close"]
    if not pd.isna(row["Open"]):
        return True, row["Open"]
    return False, None

def remove_conflicting_values(self, 
                              created_timestamps: Set, 
                              created_base_currencies: Set, 
                              created_quote_currencies: Set):
    delete_qs = Rate.objects.filter(timestamp__in=created_timestamps,
                                    base_currency__in=created_base_currencies,
                                    quote_currency__in=created_quote_currencies)
    if (delete_qs):
        self.stdout.write(self.style.WARNING(f"\nFound {len(delete_qs)} conflicting values in database. Updating with new values."))
        delete_qs.delete()
    else:
        self.stdout.write(self.style.WARNING(f"No conflicting values found in database."))

