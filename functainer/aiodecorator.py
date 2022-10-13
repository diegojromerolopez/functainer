from functools import wraps


from functainer.func2functainer.aio import aiofunc2functainer


def aiofunctainerize(**kwargs):
    async def decorator(function):
        @wraps(function)
        async def wrapper():
            return await aiofunc2functainer(function=function, **kwargs)
        return wrapper
    return decorator
