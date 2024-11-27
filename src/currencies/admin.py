from django.contrib import admin

from .models import (
    Currency,
    Rate,
)

# Register your models here.
class NoneValueFilter(admin.SimpleListFilter):
    title = ('Exchange rates period')
    parameter_name = 'time'

    def lookups(self, request, model_admin):
        return (
            ('daily', ('Day')),
            ('hourly', ('Hour')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'daily':
            return queryset.filter(time__isnull=True)  # daily values with null time
        elif value == 'hourly':
            return queryset.filter(time__isnull=False)  # hourly values without null time
        return queryset  # unfiltered queryset by default

class RateAdmin(admin.ModelAdmin):
    list_display = ['base_currency', 'quote_currency', 'exchange_rate', 'date', 'time']
    search_fields = ['base_currency__code']
    list_filter = ['base_currency__code', 'quote_currency__code', NoneValueFilter]
    ordering = ['-date', '-time']


admin.site.register(Currency)
admin.site.register(Rate, RateAdmin)
