import geojson


def to_geojson(out_path, fatalities):
  """Writes a CalTopo-compatible GeoJSON file to out_path."""
  features = []
  for f in fatalities:
    description_lines = [f.event_url]
    if f.forecast_url:
      description_lines.append(f.forecast_url)
    f = geojson.Feature(geometry=geojson.Point((f.longitude, f.latitude)),
                        properties={
                            'title': f.datetime,
                            'description': '\n'.join(description_lines),
                            'marker-color': '#00FF00',
                        })
    features.append(f)
  feature_collection = geojson.FeatureCollection(features)
  with open(out_path, 'w') as f:
    geojson.dump(feature_collection, f)
