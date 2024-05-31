#!/usr/bin/env python3
""" Redis exercise"""
import redis
import requests
from functools import wraps
from typing import Callable


store = redis.Redis()
""" Redis instance for caching and tracking requests."""


def data_cacher(method: Callable) -> Callable:
    """ Decorator that caches the output of a method."""
    @wraps(method)
    def invoker(url) -> str:
        """ Invoker function that caches the output of fetched data."""
        store.incr(f'count:{url}')
        result_redis = store.get(f'result:{url}')
        if result_redis:
            return result_redis.decode('utf-8')
        result_redis = method(url)
        store.set(f'count:{url}', 0)
        store.setex(f'result:{url}', 10, result_redis)
        return result_redis
    return invoker


@data_cacher
def get_page(url: str) -> str:
    """ Fetches the content of a web page."""
    return requests.get(url).text
