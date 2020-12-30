import btac
import export


def main():
  fatalities = btac.fetch_fatalities()
  export.to_geojson('out.json', fatalities)


if __name__ == "__main__":
  main()
