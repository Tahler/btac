import os

import btac
import export

_OUT_DIR = 'out'


def main():
  fatalities = btac.fetch_fatalities()
  os.makedirs(_OUT_DIR, exist_ok=True)
  export.to_geojson(f'{_OUT_DIR}/fatalities.json', fatalities)


if __name__ == "__main__":
  main()
