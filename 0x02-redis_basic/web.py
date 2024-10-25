#!/usr/bin/env python3
""" Caching request module """
import redis
import requests
from functools import wraps
from typing import Callable


def track_get_page(fn: Callable) -> Callable:
    """ Decorator for get_page """
    @wraps(fn)
    def wrapper(url: str) -> str:
        """ check whether a url's data is cached """
        cli = redis.Redis()
        cli.incr(f'count:{url}')
        cached_pg = cli.get(f'{url}')
        if cached_pg:
            return cached_pg.decode('utf-8')
        response = fn(url)
        cli.set(f'{url}', response, 10)
        return response
    return wrapper


@track_get_page
def get_page(url: str) -> str:
    """ Makes a http request to a given endpoint """
    resp = requests.get(url)
    return resp.text
