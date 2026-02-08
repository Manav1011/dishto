from django.db import models
from core.models import TimeStampedModel, Outlet
from Menu.models import MenuItem
from dishto.GlobalUtils import generate_unique_hash
from decimal import Decimal

# Create your models here.


class OrderItem(TimeStampedModel):
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"

class Order(TimeStampedModel):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    )
    
    outlet = models.ForeignKey(Outlet, on_delete=models.CASCADE)    
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(null=True, blank=True)
    order_items = models.ManyToManyField('OrderItem', related_name='orders', blank=True, help_text="Items included in this order")
    slug = models.SlugField(unique=True, null=True, blank=True)
    inventory_transactions = models.ManyToManyField('Inventory.InventoryTransaction', blank=True, related_name='order_items', help_text="Inventory transactions related to this order item")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_hash()
        super(Order, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"Order - {self.outlet.name} - {self.order_date}"