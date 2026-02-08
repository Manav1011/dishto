from django.contrib import admin
from .models import Franchise, Outlet, OutletSliderImage, Feature, OutletFeatureRequest, OutletFeatureHistory
# Register your models here.

admin.site.register(Franchise)
admin.site.register(Outlet)
admin.site.register(OutletSliderImage)
admin.site.register(Feature)
admin.site.register(OutletFeatureRequest)
admin.site.register(OutletFeatureHistory)