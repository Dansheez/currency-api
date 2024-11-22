from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.forms.models import model_to_dict

from typing import List, Dict, Tuple
from itertools import permutations
import yfinance as yf

from currencies.models import Rate, Currency

valid_periods = ["1d", "5d", "1mo", "3mo" "6mo", "1y", "2y", "5y", "10y", "ytd", "max"] 
valid_intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"]

class Command(BaseCommand):
    help = "Populate local database with data from yfinance module"

    def add_arguments(self, parser):
        # positonal argument
        parser.add_argument("currency_symbols", type=str, help="Currencies to load separated by comas without spaces")

        # named (optional) arguments
        parser.add_argument("-p", "--period", type=str, help=f"Time period to download.\nValid periods are: {valid_periods}.\nDefault: 1d")
        parser.add_argument("-i", "--interval", type=str, help=f"Data interval.\nValid intervals are: {valid_intervals}.\nDefault: 1h")

    def handle(self, *args, **options):
        currency_symbols = options["currency_symbols"].split(",")
        if len(currency_symbols) < 2:
            raise CommandError(f"Not enough currency symbols passed (need at least two).")
        for symbol in currency_symbols:
            if len(symbol) != 3:
                raise CommandError(f"Received invalid currency symbol '{symbol}'. Make sure all symbols you pass are exactly three characters long.")

        period = options["period"] if options["period"] else "1d"
        if period not in valid_periods:
            raise CommandError(f"Received invalid period argument of {period}.\nValid periods are: {valid_periods}.")
        interval = options["interval"] if options["interval"] else "1h"
        if interval not in valid_intervals:
            raise CommandError(f"Received invalid interval argument of {interval}.\nValid intervals are: {valid_intervals}.")

        # [{'code': EUR', 'id': 1}, {'code': 'USD', 'id': 2}, ...]
        currency_list = list(Currency.objects.values('code', 'id'))
        ticker_dict = generate_yfinance_tickers(currency_symbols, period, interval)
        model_instances = parse_data_from_yfinance(self, ticker_dict, currency_list)
        self.stdout.write(f"Creating {len(model_instances)} instances of Rate model.")
        Rate.objects.bulk_create(model_instances)
        self.stdout.write(self.style.SUCCESS(f"Succesfully populated the database."))

def parse_data_from_yfinance(self, ticker_dict: Dict, currency_list: List) -> List:
    """
    Fishes out relevant informations from data dictionary and creates a list of models for bulk creation.
    Parameters:
        ticker_dict (dict): nested dictionary in format of {"<timestamp1>": {"<ticker1>": <exchange_rate1>", 
                                                                            "<ticker2>": <exchange_rate2>"}, ...,}
        currency_list (list): list of dictionaries in format of [{"code": "EUR", "id": 1}, ...]
    Returns:
        model_instances (list): list of model instances for bulk creation.
    """
    model_instances = []
    for timestamp, tickers in ticker_dict.items():
        for ticker, exchange_rate in tickers.items():
            # split ticker
            ticker = ticker.strip("=X")
            base_currency = ticker[:3]
            quote_currency = ticker[3:]
            # check for missing exchange rate
            if type(exchange_rate) is not float:
                self.stdout.write(self.style.WARNING(f"Received non float exchange rate for {ticker} at timestamp {timestamp}. Possibly a 'NaN' value ({exchange_rate}). Skipping..."))
                continue

            base_currency_id, currency_list = get_currency_id(self, base_currency, currency_list)
            quote_currency_id, currency_list = get_currency_id(self, quote_currency, currency_list)

            model_instances.append(Rate(timestamp=timestamp.to_pydatetime(),
                                        base_currency=Currency.objects.filter(id=base_currency_id).first(),
                                        quote_currency=Currency.objects.filter(id=quote_currency_id).first(),
                                        exchange_rate=exchange_rate))
    return model_instances

def generate_yfinance_tickers(currency_symbols: List, period: str, interval: str) -> Dict:
    """
    Generates ticker label for every possible permutation of passed list elements.
    Ticker label format is "<base><quote>=X" (i.e.: "EURUSD=X" for exchanging EURO to US Dollar)
    Parameters:
        currency_symbols (list): in format of ["EUR", "USD", ...]
    Returns:
        ticker_dict (dict): nested dictionary in format of {"<timestamp1>": {"<ticker1>": <exchange_rate1>", 
                                                                            "<ticker2>": <exchange_rate2>"}, ...,}
    """
    currency_pairs = permutations(currency_symbols, 2)
    exchange_tickers = []
    for currency_pair in currency_pairs:
        # yfinance accepts tickers in format of "EURUSD=X"
        exchange_tickers.append(f"{currency_pair[0]}{currency_pair[1]}=X")
    # NOTE: probably another function? (get_data)
    df = yf.download(exchange_tickers, period=period, interval=interval)
    df = df["Close"] # take only the last exchange rate value
    df_dict = df.to_dict("index") # timestamp as index -> nested dictionary
    return df_dict

def get_currency_id(self, searched_currency: str, currency_list: List) -> Tuple[int, List]:
    """
    Checks if currency symbol is found in passed currency list argument.
    If such symbol is not found creates one, updates currency list and returns it's id.
    Parameters:
        searched_currency (str): symbol in format of "EUR", "USD", ...
        currency_list (list): list of dictionaries in format of [{"code": "EUR", "id": 1}, ...]
    Returns:
       found_id (int): id of found or created object instance
       currency_list (list): updated currency list
    """
    found_dict = next((currency for currency in currency_list if currency["code"].upper()==searched_currency), None)
    if not found_dict:
        self.stdout.write(f"Currency {searched_currency} not found in the database. Creating a new instance...")
        obj = Currency.objects.create(code=searched_currency.upper())
        found_dict = model_to_dict(obj, fields=[field.name for field in obj._meta.fields])
        currency_list.append(found_dict)
    found_id = found_dict["id"]
    return (found_id, currency_list)
