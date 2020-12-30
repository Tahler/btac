"""btac (Bridger-Teton Avalanche Center) describes types from their site."""


class Fatality:

  # TODO: Add other fields, including the number of people caught and/or killed.
  def __init__(self, datetime: str, latitude: float, longitude: float):
    self.datetime = datetime
    self.latitude = latitude
    self.longitude = longitude
