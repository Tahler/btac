import bs4
import diskcache
import requests

_CACHE = diskcache.Cache('.cache/html')


def fetch_static_soup(url, params=None):
  html = _fetch_static(url, params)
  return bs4.BeautifulSoup(html, 'html.parser')


@_CACHE.memoize()
def _fetch_static(url, params=None):
  return _fetch(url, params)


def _fetch(url, params=None):
  response = requests.get(url, params=params)
  return response.content
