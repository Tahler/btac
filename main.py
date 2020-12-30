import re

import btac
import scrape

_HOST = 'https://www.jhavalanche.org'


def main():
  urls = _fetch_event_urls()
  events = [_extract_fatality(url) for url in urls[-2:]]
  print(events)


def _fetch_event_urls():
  soup = scrape.fetch_static_soup(f'{_HOST}/dateFatalities')
  name_cells = soup.select('td[data-label="Name"] > a')
  event_paths = [a['href'] for a in name_cells]
  urls = [f'{_HOST}/{path}' for path in event_paths]
  return urls


_DATETIME_PATTERN = re.compile(r'Date/Time: (\d+\/\d+\/\d+\ \d+:\d+:\d+)')
_LATITUDE_LONGITUDE_DEGREES_PATTERN = r'(-?\d+\.\d+)'
_LATITUDE_PATTERN = re.compile(f'Lat: {_LATITUDE_LONGITUDE_DEGREES_PATTERN}')
_LONGITUDE_PATTERN = re.compile(f'Lng: {_LATITUDE_LONGITUDE_DEGREES_PATTERN}')


def _extract_fatality(url):
  soup = scrape.fetch_static_soup(url)
  # Selects the first of two columns.
  container = soup.select_one('.cell.medium-auto')
  inner_html = container.decode_contents()
  datetime = _DATETIME_PATTERN.search(inner_html).group(1)
  latitude = _LATITUDE_PATTERN.search(inner_html).group(1)
  longitude = _LONGITUDE_PATTERN.search(inner_html).group(1)
  return btac.Fatality(datetime, latitude, longitude)


if __name__ == "__main__":
  main()
