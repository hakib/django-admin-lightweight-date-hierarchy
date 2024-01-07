from django.db import models


class Sale(models.Model):
    created = models.DateTimeField()

    def __str__(self) -> str:
        return f'[{self.id}] {self.created:%Y-%m-%d}'


class SaleWithDrilldown(Sale):
    """
    We will use this model in the admin to illustrate the difference
    between date hierarchy with and without drilldown.
    """
    class Meta:
        proxy = True
        verbose_name = 'Sale model with default drilldown'


class SaleWithCustomDrilldown(Sale):
    class Meta:
        proxy = True
        verbose_name = 'Sale model with custom drilldown'
