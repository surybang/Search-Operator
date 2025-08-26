"""This script contains decorators for the project"""

from functools import wraps
from timeit import default_timer as timer
from loguru import logger


def timed(label: str):
    """Time decorators."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            t0 = timer()
            result = fn(*args, **kwargs)
            dt = timer() - t0
            logger.info(f"{label} terminé en {dt:.3f}s")
            return result
        return wrapper
    return decorator
