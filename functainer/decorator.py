from functools import wraps
from typing import List, Optional


from functainer.functainer import func2functainer


def functainerize(image: str = 'python:latest', requirements: Optional[List[str]] = None):
    def decorator(function):
        @wraps(function)
        def wrapper():
            return func2functainer(
                function=function,
                image=image,
                requirements=requirements
            )
        return wrapper
    return decorator
