from django.contrib import admin
from .models import Ingredient, Order, OrderItem, InventoryTransaction
# Register your models here.

admin.site.register(Ingredient)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(InventoryTransaction)