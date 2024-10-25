#!/usr/bin/env python3
""" using the Redis NoSQL data storage """
from functools import wraps
from typing import Any, Callable, Union
import redis
import uuid


def count_calls(method: Callable) -> Callable:
    """ Tracks the number of calls """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """ returns the given method """

        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """ Tracks the call details """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """ Returns the method's output """
        in_k = '{}:inputs'.format(method.__qualname__)
        out_k = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_k, str(args))
        out = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_k, out)
        return out
    return invoker


def replay(fun: Callable) -> None:
    """ Displays the call history """
    if fun is None or not hasattr(fun, '__self__'):
        return
    redis_store = getattr(fun.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fun.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


class Cache:
    """ Represents an object for storing data """

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data:  Union[str, bytes, int, float]) -> str:
        """ Stores a value in a Redis data storage """
        d_key = str(uuid.uuid4())
        self._redis.set(d_key, data)
        return d_key

    def get(
            self,
            key: str,
            fun: Callable = None,
            ) -> Union[str, bytes, int, float]:
        """ Retrieves a value from a Redis data """
        data = self._redis.get(key)
        return fun(data) if fun is not None else data

    def get_str(self, key: str) -> str:
        """ Retrieves a string value from a Redis data """
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """ Retrieves an integer value from a Redis data """
        return self.get(key, lambda x: int(x))
