from ninja import Schema

class CurrencyListSchema(Schema):
    # List -> CurrencyOut
    code: str

class RateDetailSchema(Schema):
    # Detail => RateOut
    currency_pair: str
    exchange_rate: float
