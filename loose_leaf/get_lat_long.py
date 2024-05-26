import requests
import json
from environs import Env

def get_first_result_details(json_data):
    # Parse the JSON data
    data = json.loads(json_data)
    
    # Check if the status is "OK" and if there is at least one result
    if data['status'] == 'OK' and len(data['results']) > 0:
        first_result = data['results'][0]
        name = first_result['name']
        lat = first_result['geometry']['location']['lat']
        lng = first_result['geometry']['location']['lng']
        return name, lat, lng
    else:
        return None, None, None

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Set up the API request parameters
BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
query = "indigo hotel"
query = "burger king"
query = "ruth ann's"
city = "Columbus"
state = "GA"
params = {
    'query': query,
    'region': f"{city}, {state}",
    'key': MAPS_API_KEY
}
headers = {
    'Accept': 'application/json'
}

# Make the API request
response = requests.request("GET", base_url, headers=headers, params=params)

# Get the JSON response
json_response = response.text

# Call the get_first_result_details function to extract details from the first result
name, lat, lng = get_first_result_details(json_response)

# Print the name and lat/long of the first result
if name:
    print("Name:", name)
    print("Latitude:", lat)
    print("Longitude:", lng)
else:
    print("No results found.")

# Print the total number of results
data = json.loads(json_response)
total_results = len(data['results'])
print("Total results:", total_results)