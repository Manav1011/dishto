"""
URL configuration for dishto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from fastapi import APIRouter
from .views import root, healthcheck
from Menu.views import router as menu_router
from core.views import end_user_router, restaurant_router
from Inventory.views import inventory_router
from Ordering.views import ordering_router
from Profile.views import router as profile_router
from django.conf import settings
from django.conf.urls.static import static


# django urls

urlpatterns = [path("admin/", admin.site.urls)]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

base_router_open = APIRouter(prefix="/open")
# end user urls
base_router_open.include_router(end_user_router)

# Protected routes
base_router_protected = APIRouter(prefix="/protected")
base_router_protected.add_api_route(
    "/healthcheck", healthcheck, methods=["GET"], name="healthcheck"
)
# restaurant urls
base_router_protected.include_router(restaurant_router)
# menu urls
base_router_protected.include_router(menu_router)
# profile urls
base_router_protected.include_router(profile_router)
# inventory urls
base_router_protected.include_router(inventory_router)
# ordering urls
base_router_protected.include_router(ordering_router)
