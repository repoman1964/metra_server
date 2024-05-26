import requests
import json
from environs import Env

def get_result_details(json_data, distance_data, radius):
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
                result_details.append((name, lat, lng, distance, city, state))

        # Sort the result_details list based on the distance (ascending order)
        result_details.sort(key=lambda x: x[3])

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

# Call the get_result_details function to extract details from the results
result_details = get_result_details(json_response, distance_json_response, radius)

# Print the details of each result
if result_details:
    print("Results within Columbus, GA and within the specified radius (ordered by distance):")
    for i, details in enumerate(result_details, start=1):
        name, lat, lng, distance, city, state = details
        print(f"Result {i}:")
        print("Name:", name)
        print("City:", city)
        print("State:", state)
        print("Latitude:", lat)
        print("Longitude:", lng)
        print("Distance:", f"{distance} meters")
        print()
else:
    print("No results found within Columbus, GA and within the specified radius.")

# Print the total number of results
total_results = len(result_details)
print("Total results within Columbus, GA and within the specified radius:", total_results)