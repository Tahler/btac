import datetime
import math

import geojson


def to_geojson(out_path, fatalities):
  """Writes a CalTopo-compatible GeoJSON file to out_path."""
  features = []
  dates = [f.date for f in fatalities]
  earliest = min(dates)
  latest = max(dates)
  num_days = (latest - earliest).days

  def _gradient(date: datetime.date) -> str:
    since_earliest = (date - earliest).days
    red_ratio = since_earliest / num_days
    r_value = math.floor(red_ratio * 127) + 128
    return '#%02x%02x%02x' % (r_value, 0, 0)

  for f in fatalities:
    description_lines = [f.event_url]
    if f.forecast_url:
      description_lines.append(f.forecast_url)
    hex_color = _gradient(f.date)
    f = geojson.Feature(geometry=geojson.Point((f.longitude, f.latitude)),
                        properties={
                            'title': f.date.isoformat(),
                            'description': '\n'.join(description_lines),
                            'marker-color': hex_color,
                            'marker-symbol': 'danger',
                        })
    features.append(f)
  feature_collection = geojson.FeatureCollection(features)
  with open(out_path, 'w') as f:
    geojson.dump(feature_collection, f)
