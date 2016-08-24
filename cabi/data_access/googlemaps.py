import googlemaps
import os


def get_loc_info(location):
    gmaps = googlemaps.Client(key=os.environ["GMAPS_KEY"])

    # The bounds, which roughly surround DC and the nearby areas with Capital
    # Bikeshare, give preference to returning results from this area. This
    # allows leaving the city off of the entered address.
    results = gmaps.geocode(location, bounds={
        "northeast": (39.294891, -76.757937),
        "southwest": (38.698693, -77.299981)})

    return results[0]
