from django.db import models
from django.http import Http404

# Create your models here.
class Currency(models.Model):
    # id
    code = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return f"{self.code}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.code:
            self.code = self.code.upper()

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)

class Rate(models.Model):
    # id 
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="base_currency")
    quote_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="quote_currency")
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=3)
    timestamp = models.DateTimeField()

    @property
    def currency_pair(self):
        return f"{self.base_currency}{self.quote_currency}"

    @classmethod
    def get_latest(cls, **filters):
        return cls.objects.filter(**filters).order_by("-timestamp").first() or None