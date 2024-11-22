from django.contrib import admin

from .models import (
    Currency,
    Rate,
)

# Register your models here.
class RateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'quote_currency', 'exchange_rate', 'timestamp']
    search_fields = ['base_currency__code']
    list_filter = ['base_currency__code', 'quote_currency__code']

admin.site.register(Currency)
admin.site.register(Rate, RateAdmin)
