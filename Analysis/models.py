from django.db import models
from core.models import TimeStampedModel
from Inventory.models import Order
from Menu.models import Outlet
from dishto.GlobalUtils import generate_unique_hash

# Create your models here.

class MonthlyBillingCycle(TimeStampedModel):
    """
    Represents a monthly billing cycle for an outlet, containing all orders for that month.
    """
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(help_text="Month number (1-12)")
    year = models.PositiveSmallIntegerField(help_text="Year of the billing cycle")
    orders = models.ManyToManyField(Order, related_name="billing_cycles")
    slug = models.SlugField(unique=True, null=True, blank=True)

    class Meta:
        unique_together = ("outlet", "month", "year")
        verbose_name = "Monthly Billing Cycle"
        verbose_name_plural = "Monthly Billing Cycles"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(MonthlyBillingCycle, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.outlet} - {self.month:02d}/{self.year}"