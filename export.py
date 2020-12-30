import geojson


def to_geojson(out_file, positions):
  points = [geojson.Point(p) for p in positions]
  features = [geojson.Feature(geometry=p) for p in points]
  feature_collection = geojson.FeatureCollection(features)
  with open(out_file, 'w') as f:
    geojson.dump(feature_collection, f)
