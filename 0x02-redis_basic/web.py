#!/usr/bin/env python3
""" Redis exercise"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
""" Redis store instance."""


def data_cacher(method: Callable) -> Callable:
    """Decorator that caches the output of a function."""
    @wraps(method)
    def invoker(url) -> str:
        """ Invoker function that caches the output of fetched data."""
        redis_store.incr(f'count:{url}')
        result = redis_store.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_store.set(f'count:{url}', 0)
        redis_store.setex(f'result:{url}', 10, result)
        return result
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """ Fetches the page at the given URL and returns its content
    From HTML FILE
    """
    return requests.get(url).text
