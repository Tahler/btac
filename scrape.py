import bs4
import diskcache
import requests

_CACHE = diskcache.Cache('.cache/html')


def fetch_static_soup(url):
  html = _fetch_static(url)
  return bs4.BeautifulSoup(html, 'html.parser')


@_CACHE.memoize()
def _fetch_static(url):
  return _fetch(url)


def _fetch(url):
  response = requests.get(url)
  return response.content
