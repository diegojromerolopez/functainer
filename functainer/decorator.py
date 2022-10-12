from functools import wraps
from typing import List, Optional


from functainer.functainer import func2functainer


def functainerize(**kwargs):
    def decorator(function):
        @wraps(function)
        def wrapper():
            return func2functainer(function=function, **kwargs)
        return wrapper
    return decorator
