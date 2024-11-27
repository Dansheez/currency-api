from ninja import Router
from ninja.errors import HttpError

from typing import List

from .models import Currency, Rate
from .schemas import CurrencyListSchema, RateDetailSchema

router = Router()

@router.get("", response=List[CurrencyListSchema])
def list_currencies(request):
    qs = Currency.objects.all()
    return qs

@router.get("/{BASE}/{QUOTE}/", response=RateDetailSchema)
def detail_rate(request, BASE:str, QUOTE:str):
    obj = Rate.get_latest(base_currency__code=BASE.upper(),
                          quote_currency__code=QUOTE.upper())
    if obj:
        return obj
    raise HttpError(404, f"Exchange rate for currencies '{BASE}' and '{QUOTE}' not found.")
