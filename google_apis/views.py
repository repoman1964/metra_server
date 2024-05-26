import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic
import math
from django.http import HttpResponse


# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the Places API request parameters
BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
BASE_URL_ADDRESS_SEARCH = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
BASE_URL_PLACE_ID_SEARCH = "https://maps.googleapis.com/maps/api/place/details/json"

def query_google_places_by_name(point_name):
    """
    Query the Google Places API for locations matching the place_location within a given radius from the reference_location.
    """

    reference_location="32.463307,-84.993284"
    radius=2000
    params = {
        'query': point_name,
        'location': reference_location,
        'radius': radius,
        'key': MAPS_API_KEY
    }
    headers = {
        'Accept': 'application/json'
    }

    # Make the Places API request
    response = requests.get(BASE_URL_NAME_SEARCH, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()    
    return None

def query_google_places_by_address(point_address):
    """
    Query the Google Places API for locations matching the given address.
    """

   
    params = {
        'input': point_address,
        'inputtype': 'textquery',
        'key': MAPS_API_KEY
    }
    headers = {
        'Accept': 'application/json'
    }

    # Make the Places API request
    response = requests.get(BASE_URL_ADDRESS_SEARCH, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()    
    return None 

def query_google_places_by_place_id(place_id):
    """
    Query the Google Places API for locations matching the given address.  """

   
    params = {
        'place_id': place_id,
        'key': MAPS_API_KEY
    }
    headers = {
        'Accept': 'application/json'
    }

    # Make the Places API request
    response = requests.get(BASE_URL_PLACE_ID_SEARCH, headers=headers, params=params)
    print(response.text)

    if response.status_code == 200:
        return response.json()    
    return None
     