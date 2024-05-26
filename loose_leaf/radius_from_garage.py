import requests
import json
from environs import Env

def get_result_details(json_data, distance_data):
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
            distance = distances['rows'][0]['elements'][i]['distance']['text']
            result_details.append((name, lat, lng, distance))
        return result_details
    else:
        return []

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the Places API request parameters
BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
query = "indigo"
location = "32.4720218,-84.9948138"  # Latitude and longitude of the reference point
radius = 1  # Radius in meters
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

# Call the get_result_details function to extract details from the results
result_details = get_result_details(json_response, distance_json_response)

# Print the details of each result
if result_details:
    print("Results within the specified radius:")
    for i, details in enumerate(result_details, start=1):
        name, lat, lng, distance = details
        print(f"Result {i}:")
        print("Name:", name)
        print("Latitude:", lat)
        print("Longitude:", lng)
        print("Distance:", distance)
        print()
else:
    print("No results found within the specified radius.")

# Print the total number of results
data = json.loads(json_response)
total_results = len(data['results'])
print("Total results within the specified radius:", total_results)