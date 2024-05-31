#!/usr/bin/env python3
""" Redis exercise"""
from functools import wraps
from typing import Any, Callable, Union
import redis
import uuid


def count_calls(method: Callable) -> Callable:
    """ Decorator that increments the count of how many times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """ Wrapper function that increments the count of how many times a method is called."""

        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """ Decorator that stores the history of inputs and outputs for a method."""
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """ Invoker function that stores the history of inputs and outputs for a method."""
        input_key = '{}:inputs'.format(method.__qualname__)
        output_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    """ Displays the history of calls of a particular function."""
    if fn is None or not hasattr(fn, '__self__'):
        return
    store = getattr(fn.__self__, '_redis', None)
    if not isinstance(store, redis.Redis):
        return
    fn_name = fn.__qualname__
    inKey = '{}:inputs'.format(fn_name)
    outKey = '{}:outputs'.format(fn_name)
    call_count = 0
    if store.exists(fn_name) != 0:
        call_count = int(store.get(fn_name))
    print('{} was called {} times:'.format(fn_name, call_count))
    fn_input = store.lrange(inKey, 0, -1)
    fn_outputs = store.lrange(outKey, 0, -1)
    for f_input, f_output in zip(fn_input, fn_outputs):
        print('{}(*{}) -> {}'.format(
            fn_name,
            f_input.decode("utf-8"),
            f_output,
        ))


class Cache:
    """ Cache class that stores instances of Redis."""

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data:  Union[str, bytes, int, float]) -> str:
        """ Stores data in a Redis data storage."""
        data = str(uuid.uuid4())
        self._redis.set(data, data)
        return data

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        """ Retrieves data from a Redis data storage."""
        data_key = self._redis.get(key)
        return fn(data_key) if fn is not None else data_key

    def get_str(self, key: str) -> str:
        """ Retrieves a string value from a Redis data storage."""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """ Retrieves an integer value from a Redis data storage."""
        return self.get(key, lambda x: int(x))
