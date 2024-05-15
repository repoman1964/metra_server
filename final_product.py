import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic

def is_within_area(point, nw_coords, ne_coords, sw_coords, se_coords):
    # Define the points
    point = Point(point)
    nw_point = Point(nw_coords)
    ne_point = Point(ne_coords)
    sw_point = Point(sw_coords)
    se_point = Point(se_coords)

    # Define the polygon
    polygon = Polygon([nw_point, ne_point, se_point, sw_point, nw_point])

    # Check if the point is within the polygon
    if polygon.contains(point):
        return True, 0.0

    # Calculate the nearest distance to the polygon edges
    # Find the nearest point on the polygon to the point
    nearest_point = nearest_points(point, polygon.boundary)[1]

    # Calculate the geodesic distance between the points in miles
    distance = geodesic((point.y, point.x), (nearest_point.y, nearest_point.x)).miles

    return False, distance, (nearest_point.y, nearest_point.x)

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
            if 'Columbus' in result['formatted_address'] and 'GA' in result['formatted_address'] and query in name.lower() and distance <= radius:
                city = 'Columbus'
                state = 'GA'
                
                # Retrieve the street address using the Geocoding API
                geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={MAPS_API_KEY}"
                geocode_response = requests.get(geocode_url)
                geocode_data = json.loads(geocode_response.text)
                
                if geocode_data['status'] == 'OK' and len(geocode_data['results']) > 0:
                    street_address = geocode_data['results'][0]['formatted_address']
                else:
                    street_address = 'N/A'
                
                # Check if the location is within the defined polygon
                within_area, distance_to_edge, nearest_edge_coords = is_within_area((lat, lng), nw_coords, ne_coords, sw_coords, se_coords)

                if not within_area:
                    # Retrieve the human-readable address of the nearest edge
                    nearest_edge_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={nearest_edge_coords[0]},{nearest_edge_coords[1]}&key={MAPS_API_KEY}"
                    nearest_edge_response = requests.get(nearest_edge_url)
                    nearest_edge_data = json.loads(nearest_edge_response.text)
                    
                    if nearest_edge_data['status'] == 'OK' and len(nearest_edge_data['results']) > 0:
                        nearest_edge_address = nearest_edge_data['results'][0]['formatted_address']
                    else:
                        nearest_edge_address = 'N/A'
                else:
                    nearest_edge_address = 'N/A'
                
                result_details.append((name, lat, lng, street_address, within_area, distance_to_edge, nearest_edge_address))

        # Sort the result_details list based on the distance (ascending order)
        result_details.sort(key=lambda x: x[5])

        return result_details
    else:
        return []

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the Places API request parameters
base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
query = "sharks"
location = "32.4720218,-84.9948138"  # Latitude and longitude of the reference point
radius = 3000  # Radius in meters (3 km)
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
nw_coords = (32.472546064404, -84.99463382471089)
ne_coords = (32.47244649932993, -84.99186578507934)
sw_coords = (32.46105423026278, -84.99638061912495)
se_coords = (32.46290893943292, -84.99041537310289)

# Call the get_result_details function to extract details from the results
result_details = get_result_details(json_response, distance_json_response, radius, nw_coords, ne_coords, sw_coords, se_coords)

# Print the details of each result
if result_details:
    print("Results within Columbus, GA and within the specified radius (ordered by distance to the polygon edge):")
    for i, details in enumerate(result_details, start=1):
        name, lat, lng, address, within_area, distance_to_edge, nearest_edge_address = details
        print(f"Result {i}:")
        print("Name:", name)
        print("Street Address:", address)
        print("Latitude:", lat)
        print("Longitude:", lng)
        print("Within Shuttle Service Area:", within_area)
        print("Distance to Polygon Edge:", f"{distance_to_edge:.2f} miles")
        if not within_area:
            print("Nearest Edge Address:", nearest_edge_address)
        print()
else:
    print("No results found within Columbus, GA and within the specified radius.")

# Print the total number of results
total_results = len(result_details)
print("Total results within Columbus, GA and within the specified radius:", total_results)