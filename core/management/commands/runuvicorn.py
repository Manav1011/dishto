from django.core.management.base import BaseCommand
import uvicorn

class Command(BaseCommand):
    help = 'Run the ASGI server using Uvicorn'

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', default='127.0.0.1:8000')

    def handle(self, *args, **options):
        addrport = options['addrport']
        host, port = addrport.split(":")        
        uvicorn.run("dishto.asgi:application", host=host, port=int(port), reload=True)