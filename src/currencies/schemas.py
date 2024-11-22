from ninja import Schema

class CurrencyListSchema(Schema):
    # List -> CurrencyOut
    code: str
