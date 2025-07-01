from contextlib import asynccontextmanager

from cryptography.hazmat.primitives import serialization

from django.conf import settings
from core.utils.logger import logger
from dishto.GlobalUtils import qdrant_client_
from qdrant_client.models import VectorParams, Distance
from core.utils.constants import MENUITEM_COLLECTION_NAME


@asynccontextmanager
async def lifespan(app):
    """Asynchronous context manager to manage the lifespan of the application.
    """
    # create qdrant collections
    if not qdrant_client_.collection_exists(MENUITEM_COLLECTION_NAME):
        qdrant_client_.create_collection(
            collection_name=MENUITEM_COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
    yield