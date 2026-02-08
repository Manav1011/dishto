from django.contrib import admin
from .models import Ingredient, InventoryTransaction
# Register your models here.

admin.site.register(Ingredient)
admin.site.register(InventoryTransaction)