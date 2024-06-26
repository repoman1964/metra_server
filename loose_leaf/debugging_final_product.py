import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic
import math

# Define the service area points
boundary_points = {
    "nw": (32.47361181679043, -84.99502757805325),
    "ne": (32.474305395776845, -84.99039374856852),
    "sw": (32.461455254991144, -84.99640233868355),
    "se": (32.46287557552805, -84.99040377675384)
}


# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the Places API request parameters
BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def get_coordinates(    query_location = "sharks"):

    query_location = "sharks"
    reference_location = "32.463307,-84.993284" # Latitude and longitude of the reference point (shuttle garage)

    query = query_location
    location = reference_location
    radius = 2000  # Radius in meters (2 km) from reference_location

    params = {
        'query': query,
        'location': location,
        'radius': radius,
        'key': MAPS_API_KEY
    }
    headers = {
        'Accept': 'application/json'
    }

    # Make the Places API request
    response = requests.request("GET", base_url, headers=headers, params=params)


def is_within_area(point, boundary_points):
    """
    Check if a given point is within a polygon defined by the boundary points.

    Parameters:
    - point (tuple): The coordinates of the point to check.
    - boundary_points (dict): A dictionary containing the coordinates of the boundary points.
    
    Returns:
    - bool: True if the point is within the polygon, False otherwise.
    """
    # Convert the input point to a shapely Point
    point = Point(point)

    # Convert the boundary points to shapely Points and create the polygon
    polygon = Polygon([boundary_points["nw"], boundary_points["ne"], boundary_points["se"], boundary_points["sw"]])

    # Check if the point is within the polygon
    return polygon.contains(point)

# Example usage
point_to_check = (32.4700, -84.9920)
is_within = is_within_area(point_to_check, boundary_points)
print(f"The point {point_to_check} is within the area: {is_within}")

def get_result_details(json_data, distance_data, radius, nw_coords, ne_coords, sw_coords, se_coords):
    # Parse the JSON data
    data = json.loads(json_data)
    distances = json.loads(distance_data)

    # Check if the status is "OK"
    if data['status'] == 'OK' and distances['status'] == 'OK':
        results = data['results']
        result_details = []
        for i, result in enumerate(results):
            name = result['name']
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            distance = distances['rows'][0]['elements'][i]['distance']['value']  # Get distance in meters

            # Check if the result is within Columbus, GA, contains the query term in the name, and is within the specified radius
            if 'Columbus' in result['formatted_address'] and 'GA' in result['formatted_address'] and query.lower() in name.lower() and distance <= radius:
                city = 'Columbus'
                state = 'GA'
                
                # Retrieve the street address using the Geocoding API
                geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={MAPS_API_KEY}"
                geocode_response = requests.get(geocode_url)
                geocode_data = json.loads(geocode_response.text)
                
                if geocode_data['status'] == 'OK' and len(geocode_data['results']) > 0:
                    street_address = geocode_data['results'][0]['formatted_address']
                    street_name = next((component['long_name'] for component in geocode_data['results'][0]['address_components'] if 'route' in component['types']), 'N/A')
                else:
                    street_address = 'N/A'
                    street_name = 'N/A'
                
                # Check if the location is within the defined polygon
                within_area, distance_to_edge, nearest_edge_coords = is_within_area((lat, lng), nw_coords, ne_coords, sw_coords, se_coords)

                if not within_area:
                    # Convert the distance to city blocks
                    blocks_to_edge = miles_to_city_blocks(distance_to_edge)

                    # Calculate the general direction to the nearest edge point
                    direction_to_edge = calculate_direction((lat, lng), nearest_edge_coords)
                    
                    # Retrieve the human-readable address of the nearest edge
                    nearest_edge_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={nearest_edge_coords[0]},{nearest_edge_coords[1]}&key={MAPS_API_KEY}"
                    nearest_edge_response = requests.get(nearest_edge_url)
                    nearest_edge_data = json.loads(nearest_edge_response.text)
                    
                    if nearest_edge_data['status'] == 'OK' and len(nearest_edge_data['results']) > 0:
                        nearest_edge_address = nearest_edge_data['results'][0]['formatted_address']
                        nearest_edge_street_name = next((component['long_name'] for component in nearest_edge_data['results'][0]['address_components'] if 'route' in component['types']), 'N/A')
                    else:
                        nearest_edge_address = 'N/A'
                        nearest_edge_street_name = 'N/A'
                else:
                    nearest_edge_address = 'N/A'
                    nearest_edge_street_name = 'N/A'
                    blocks_to_edge = 0
                    direction_to_edge = 'N/A'
                
                result_details.append((name, lat, lng, street_address, street_name, within_area, distance_to_edge, blocks_to_edge, direction_to_edge, nearest_edge_address, nearest_edge_street_name))

        # Sort the result_details list based on the distance (ascending order)
        result_details.sort(key=lambda x: x[6])

        return result_details
    else:
        return []

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the Places API request parameters
BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
query = "sharks"
# query = "2WR"
location = "32.463307,-84.993284"  # Latitude and longitude of the reference point (shuttle garage)
radius = 2000  # Radius in meters (2 km)
params = {
    'query': query,
    'location': location,
    'radius': radius,
    'key': MAPS_API_KEY
}
headers = {
    'Accept': 'application/json'
}

# Make the Places API request
response = requests.request("GET", base_url, headers=headers, params=params)

# Get the JSON response from the Places API
json_response = response.text

# Set up the Distance Matrix API request parameters
distance_base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
origins = location
destinations = '|'.join([f"{result['geometry']['location']['lat']},{result['geometry']['location']['lng']}" for result in json.loads(json_response)['results']])
distance_params = {
    'origins': origins,
    'destinations': destinations,
    'key': MAPS_API_KEY
}

# Make the Distance Matrix API request
distance_response = requests.request("GET", distance_base_url, headers=headers, params=distance_params)

# Get the JSON response from the Distance Matrix API
distance_json_response = distance_response.text

# Define the polygon coordinates
nw_coords = (32.47361181679043, -84.99502757805325)
ne_coords = (32.474305395776845, -84.99039374856852)
sw_coords = (32.461455254991144, -84.99640233868355)
se_coords = (32.46287557552805, -84.99040377675384)

# Call the get_result_details function to extract details from the results
result_details = get_result_details(json_response, distance_json_response, radius, nw_coords, ne_coords, sw_coords, se_coords)

# Print the details of each result
if result_details:
    print("Results within Columbus, GA and within the specified radius (ordered by distance to the polygon edge):")
    for i, details in enumerate(result_details, start=1):
        name, lat, lng, address, street_name, within_area, distance_to_edge, blocks_to_edge, direction_to_edge, nearest_edge_address, nearest_edge_street_name = details
        print(f"Result {i}:")
        print("Name:", name)
        print("Street Address:", address)
        print("Street Name:", street_name)
        print("Latitude:", lat)
        print("Longitude:", lng)
        print("Within Polygon:", within_area)
        if not within_area:
            print(f"Distance to Polygon Edge: {blocks_to_edge:.2f} blocks")
            print(f"Direction to Nearest Edge: {direction_to_edge}")
            print("Nearest Edge Address:", nearest_edge_address if nearest_edge_address != 'N/A' else 'Not available')
            print("Nearest Edge Street Name:", nearest_edge_street_name if nearest_edge_street_name != 'N/A' else 'Not available')
        print()
else:
    print("No results found within Columbus, GA and within the specified radius.")

# Print the total number of results
total_results = len(result_details)
print("Total results within Columbus, GA and within the specified radius:", total_results)
