"""btac (Bridger-Teton Avalanche Center) has functions to scrape their site."""

import datetime
import re
from typing import Dict, List

import bs4

import scrape

_HOST = 'https://www.jhavalanche.org'


def fetch_fatalities():
  urls = _fetch_event_urls()
  fatalities = []
  for url in urls:
    try:
      f = _extract_fatality(url)
      fatalities.append(f)
    except Exception as e:
      print(f'Could not extract fatality information from {url}: {e}')
  return fatalities


def _fetch_event_urls():
  soup = scrape.fetch_static_soup(f'{_HOST}/areaFatalities')
  table_soup = soup.select_one('table')
  rows = _extract_table(table_soup)
  return [r.event_url for r in rows]


def _extract_table(table_soup: bs4.BeautifulSoup,
                   threshold_year=1970) -> List[Dict[str, str]]:
  """Extracts the 'Teton Range' sub-table.

  Skips rows that are before the threshold_year.

  Args:
    table_soup: The <table> under the 'AVALANCHE FATALITIES BY AREA' header.
    threshold_year: Rows with a date earlier than this are excluded.
  """
  text = table_soup.find(text='Teton Range, Snake River Range & Jackson Hole')
  b = text.parent
  td = b.parent
  tr = td.parent

  thead = tr.next_sibling
  header = [th.get_text() for th in thead.select('th')]
  rows = []
  tr = thead.next_sibling
  while True:
    if tr.name != 'tr':
      break
    tds = tr.select('td')
    if len(tds) != len(header):
      break
    row = FatalityRow(header, tr)
    if row.date >= _EARLIEST_FORECAST_DATE:
      rows.append(row)
    tr = tr.next_sibling
  return rows


_EARLIEST_FORECAST_DATE = datetime.date(1999, 11, 29)


class FatalityRow:

  def __init__(self, header: List[str], tds: List[bs4.BeautifulSoup]):
    for (key, td) in zip(header, tds):
      if key == 'Date':
        value = td.get_text().strip()
        self.date = _parse_date(value)
        self.forecast_url = _format_forecast_url(self.date)
      elif key == 'Name':
        a = td.find('a')
        path = a['href']
        self.event_url = f'{_HOST}/{path}'


def _parse_date(s: str) -> datetime.date:
  for format in ['%Y', '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%Y %H:%M:%S']:
    try:
      dt = datetime.datetime.strptime(s, format)
      return dt.date()
    except ValueError:
      continue
  raise ValueError(f'failed to parse {s}')


def _format_forecast_url(date: datetime.date) -> str:
  if date < _EARLIEST_FORECAST_DATE:
    return None
  query_string = f'?data_date={date.isoformat()}&template=teton_print.tpl.php'
  return f'{_HOST}/viewTeton{query_string}'


_DATETIME_PATTERN = re.compile(r'Date/Time: (\d+\/\d+\/\d+(?:\ \d+:\d+:\d+)?)')
_LATITUDE_LONGITUDE_DEGREES_PATTERN = r'(-?\d+\.\d+)'
_LATITUDE_PATTERN = re.compile(f'Lat: {_LATITUDE_LONGITUDE_DEGREES_PATTERN}')
_LONGITUDE_PATTERN = re.compile(f'Lng: {_LATITUDE_LONGITUDE_DEGREES_PATTERN}')


def _extract_fatality(url):
  soup = scrape.fetch_static_soup(url)
  # Selects the first of two columns.
  container = soup.select_one('.cell.medium-auto')
  inner_html = container.decode_contents()
  raw_datetime = _DATETIME_PATTERN.search(inner_html).group(1)
  date = _parse_date(raw_datetime)
  latitude = _LATITUDE_PATTERN.search(inner_html).group(1)
  longitude = _LONGITUDE_PATTERN.search(inner_html).group(1)
  forecast_url = _format_forecast_url(date)
  return Fatality(date, float(latitude), float(longitude), url, forecast_url)


class Fatality:

  # TODO: Add other fields, including the number of people caught and/or killed.
  def __init__(self, date: datetime.date, latitude: float, longitude: float,
               event_url: str, forecast_url: str):
    self.date = date
    self.latitude = latitude
    self.longitude = longitude
    self.event_url = event_url
    self.forecast_url = forecast_url
