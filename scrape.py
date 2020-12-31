from typing import Dict

import bs4
import diskcache
import requests

_CACHE = diskcache.Cache('.cache/html')


def fetch_static_soup(url: str,
                      params: Dict[str, str] = None) -> bs4.BeautifulSoup:
  html = _fetch_static(url, params)
  return bs4.BeautifulSoup(html, 'html.parser')


@_CACHE.memoize()
def _fetch_static(url: str, params: Dict[str, str] = None) -> str:
  return _fetch(url, params)


def _fetch(url: str, params: Dict[str, str] = None) -> str:
  response = requests.get(url, params=params)
  return response.content
