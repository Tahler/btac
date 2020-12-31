"""btac (Bridger-Teton Avalanche Center) has functions to scrape their site."""

import datetime
import re
from typing import List, Tuple

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


def _fetch_event_urls():
  soup = scrape.fetch_static_soup(f'{_HOST}/dateFatalities')
  name_cells = soup.select('td[data-label="Name"] > a')
  event_paths = [a['href'] for a in name_cells]
  urls = [f'{_HOST}/{path}' for path in event_paths]
  return urls


_DATETIME_PATTERN = re.compile(r'Date/Time: (\d+\/\d+\/\d+(?:\ \d+:\d+:\d+)?)')
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
  return Fatality(datetime, float(latitude), float(longitude))


class Fatality:

  # TODO: Add other fields, including the number of people caught and/or killed.
  def __init__(self, datetime: str, latitude: float, longitude: float):
    self.datetime = datetime
    self.latitude = latitude
    self.longitude = longitude


def fetch_forecast(date: datetime.date) -> Forecast:
  soup = _fetch_forecast_soup(date)
  return _extract_forecast(soup)


def _fetch_forecast_soup(date: datetime.date) -> bs4.BeautifulSoup:
  return scrape.fetch_static_soup(
      f'{_HOST}/viewTeton',
      params={
          'data_date': date.isoformat(),
          # This "printer-friendly" format has minimal images.
          'template': 'teton_print.tpl.php',
      })


def _extract_forecast(soup: bs4.BeautifulSoup) -> Forecast:
  issued_at = soup.find(name='h5', text='TETON AREA FORECAST')
  strong = soup.find(name='strong', text='GENERAL AVALANCHE HAZARD')
  h5 = strong.parent
  # assert h5.name == 'h5'
  cell = h5.parent
  # assert cell.class == 'cell'
  rows = cell.select('table > tbody > tr')
  general_avalanche_hazards = []
  for row in rows:
    cells = row.select('td')
    elevation = cells[0].get_text()
    start, end = _extract_elevation_range(elevation)
    # assert elevation['data-label'] == 'Elevation'
    morning_rating = cells[1].get_text()
    # assert morning_rating['data-label'] in ('AM Rating', 'Rating')
    afternoon_rating = cells[2].get_text()
    # assert afternoon_rating['data-label'] == 'PM Rating'
    hazard = GeneralAvalancheHazard(elevation, morning_rating, afternoon_rating)
    general_avalanche_hazards.append(hazard)

  general_avalanche_advisory = ''
  forecast = Forecast(issued_at, start, end, general_avalanche_hazards,
                      general_avalanche_advisory)


_ELEVATION_RANGE_PATTERN = re.compile(r'([\d,]+)-10,500')


def _extract_elevation_range(cell: str) -> Tuple[int, int]:
  pass
  # _ELEVATION_RANGE_PATTERN.find()
  # start_elevation_feet =
  # end_elevation_feet = '9,000´-10,500´'


class Forecast:

  def __init__(self, issued_at: datetime.datetime,
               general_avalanche_hazards: List[GeneralAvalancheHazard],
               general_avalanche_advisory: str
               # TODO: Add problem types.
              ):
    self.issued_at = issued_at
    self.general_avalanche_hazards = general_avalanche_hazards
    self.general_avalanche_advisory = general_avalanche_advisory


class GeneralAvalancheHazard:

  def __init__(
      self,
      start_elevation_feet: int,
      end_elevation_feet: int,
      # TODO: Make rating an enum.
      morning_rating: str,
      afternoon_rating: str):
    self.start_elevation_feet = start_elevation_feet
    self.end_elevation_feet = end_elevation_feet
    self.morning_rating = morning_rating
    self.afternoon_rating = afternoon_rating
