from asgiref.sync import sync_to_async

async def get_queryset(func, *args, **kwargs):
    return await sync_to_async(func)(*args, **kwargs)

async def get_object(func, *args, **kwargs):
    return await sync_to_async(func)(*args, **kwargs)

async def get_related_object(instance, field_name: str):
    return await sync_to_async(lambda: getattr(instance, field_name))()

async def is_valid_async(serializer):
    return await sync_to_async(serializer.is_valid)()