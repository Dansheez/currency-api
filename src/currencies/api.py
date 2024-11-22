from django.http import Http404
from ninja import Router
from ninja.errors import HttpError

from typing import List

from .models import Currency, Rate
from .schemas import CurrencyListSchema

router = Router()

@router.get("", response=List[CurrencyListSchema])
def list_currencies(request):
    qs = Currency.objects.all()
    return qs

@router.get("/{BASE}/{QUOTE}/", response=dict)
def detail_rate(request, BASE:str, QUOTE:str):
    obj = Rate.get_latest(base_currency__code=BASE.upper(),
                          quote_currency__code=QUOTE.upper())

    if obj:
        return {
            "currency_pair": obj.currency_pair,
            "exchange_rate": float(obj.exchange_rate)
        }
    return {}
