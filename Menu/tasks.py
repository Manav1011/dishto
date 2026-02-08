from celery import shared_task
import asyncio
from .utils import generate_menu_item_embedding

@shared_task
def generate_menu_item_embedding_task(name: str, description: str, outlet_slug: str, slug:str):
    print("running generate_menu_item_embedding_task")
    asyncio.run(generate_menu_item_embedding(name=name, description=description, slug=slug, outlet_slug=outlet_slug))
