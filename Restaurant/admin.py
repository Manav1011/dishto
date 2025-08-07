from django.contrib import admin
from .models import Franchise, Outlet, MenuCategory, MenuItem
# Register your models here.

admin.site.register(Franchise)
admin.site.register(Outlet)
admin.site.register(MenuCategory)
admin.site.register(MenuItem) 
