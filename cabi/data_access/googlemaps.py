import googlemaps
import os


def get_loc_info(location):
    gmaps = googlemaps.Client(key=os.environ["GMAPS_KEY"])

    results = gmaps.geocode(location)

    return results[0]
