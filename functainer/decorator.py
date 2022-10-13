from functools import wraps


from functainer.func2functainer import func2functainer


def functainerize(**kwargs):
    def decorator(function):
        @wraps(function)
        def wrapper():
            return func2functainer(function=function, **kwargs)
        return wrapper
    return decorator
