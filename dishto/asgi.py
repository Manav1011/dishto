"""
ASGI config for dishto project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dishto.settings')
import django
django.setup()

from dishto.fastapi_setup import get_fastapi_application
from starlette.applications import Starlette
from starlette.routing import Mount



django_application = get_asgi_application()
application = get_fastapi_application()
application.mount("/", django_application)  # Mount Django at the root path

# # Combined ASGI app
# application = Starlette(routes=[
#     Mount("/api", app=fastapi_application),      # FastAPI served at /api/*
#     Mount("/", app=application),          # Django served at /
# ])