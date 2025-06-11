from asgiref.sync import sync_to_async

async def get_queryset(func, *args, **kwargs):
    return await sync_to_async(func)(*args, **kwargs)

async def get_object(func, *args, **kwargs):
    return await sync_to_async(func)(*args, **kwargs)