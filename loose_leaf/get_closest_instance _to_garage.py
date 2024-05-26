import requests
import json
from environs import Env

def get_result_details(json_data):
    # Parse the JSON data
    data = json.loads(json_data)
    
    # Check if the status is "OK"
    if data['status'] == 'OK':
        results = data['results']
        result_details = []
        for result in results:
            name = result['name']
            lat = result['geometry']['location']['lat']
            lng = result['geometry']['location']['lng']
            result_details.append((name, lat, lng))
        return result_details
    else:
        return []

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the API request parameters
BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
query = "indigo"
location = "32.463307,-84.993284"  # Latitude and longitude of the reference point
params = {
    'query': query,
    'location': location,
    'rankby': 'distance',
    'key': MAPS_API_KEY
}
headers = {
    'Accept': 'application/json'
}

# Make the API request
response = requests.request("GET", base_url, headers=headers, params=params)

# Get the JSON response
json_response = response.text

# Call the get_result_details function to extract details from the results
result_details = get_result_details(json_response)

# Print the details of each result
if result_details:
    print("Results ordered by distance:")
    for i, details in enumerate(result_details, start=1):
        name, lat, lng = details
        print(f"Result {i}:")
        print("Name:", name)
        print("Latitude:", lat)
        print("Longitude:", lng)
        print()
else:
    print("No results found.")

# Print the total number of results
data = json.loads(json_response)
total_results = len(data['results'])
print("Total results:", total_results)