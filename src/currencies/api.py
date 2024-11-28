from ninja import Router, Query, FilterSchema, Field
from ninja.errors import HttpError

from typing import List

from pydantic import model_validator

from .models import Currency, Rate
from .schemas import CurrencyListSchema, RateDetailSchema

router = Router()

# /api/currency/
@router.get("", response=List[CurrencyListSchema])
def list_currencies(request):
    qs = Currency.objects.all()
    return qs

# /api/currency/EUR/USD/
@router.get("/{BASE}/{QUOTE}/", response=RateDetailSchema)
def detail_rate(request, BASE:str, QUOTE:str):
    obj = Rate.get_latest(base_currency__code=BASE.upper(),
                          quote_currency__code=QUOTE.upper())
    if obj:
        return obj
    raise HttpError(404, f"Exchange rate for currencies '{BASE}' and '{QUOTE}' not found.")

class RateFilter(FilterSchema):
    base: str = Field(None, q='base_currency__code')
    quote: str = Field(None, q='quote_currency__code')

    @model_validator(mode='before')
    def validate_and_preprocess(cls, values):
        base = getattr(values, "base", None)
        quote = getattr(values, "quote", None)

        if base: setattr(values, "base", base.upper())
        if quote: setattr(values, "quote", quote.upper())
        return values

# /api/currency/rates?base=EUR&quote=USD
@router.get("rates/", response=List[RateDetailSchema])
def list_rate(request, filters: RateFilter=Query()):
    qs = Rate.objects.all()
    qs = filters.filter(qs)
    return qs
