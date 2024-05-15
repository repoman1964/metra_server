import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic
from django.http import JsonResponse
import math

from django.views.generic import TemplateView

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Define the polygon coordinates
nw_coords = (32.47361181679043, -84.99502757805325)
ne_coords = (32.474305395776845, -84.99039374856852)
sw_coords = (32.461455254991144, -84.99640233868355)
se_coords = (32.46287557552805, -84.99040377675384)

def miles_to_city_blocks(miles, block_length=350):
    feet_per_mile = 5280
    blocks_per_mile = feet_per_mile / block_length
    return miles * blocks_per_mile

def calculate_direction(point, nearest_edge_coords):
    delta_y = nearest_edge_coords[0] - point[0]
    delta_x = nearest_edge_coords[1] - point[1]
    angle = math.atan2(delta_y, delta_x)
    degrees = math.degrees(angle)
    
    if degrees < 0:
        degrees += 360
    
    if 45 <= degrees < 135:
        return "East"
    elif 135 <= degrees < 225:
        return "South"
    elif 225 <= degrees < 315:
        return "West"
    else:
        return "North"

def is_within_area(point):
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
        return True, 0.0, None

    # Calculate the nearest distance to the polygon edges
    # Find the nearest point on the polygon to the point
    nearest_point = nearest_points(point, polygon.boundary)[1]
    nearest_edge_coords = (nearest_point.y, nearest_point.x)

    # Calculate the geodesic distance between the points in miles
    distance = geodesic((point.y, point.x), (nearest_point.y, nearest_point.x)).miles

    return False, distance, nearest_edge_coords

def get_result_details(query, json_data, distance_data, radius, nw_coords, ne_coords, sw_coords, se_coords):
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
                location_lat = result["geometry"]["location"]["lat"]
                location_lng = result["geometry"]["location"]["lng"]
                location_point = Point(location_lat, location_lng)
                within_area, distance_to_edge, nearest_edge_coords = is_within_area(location_point)

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

def search_places(request):
    # Set up the Places API request parameters
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    query = "sharks"
    location = "32.46155548095703,-84.99342346191406"  # Latitude and longitude of the reference point (shuttle garage)
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

    # Call the get_result_details function to extract details from the results
    result_details = get_result_details(query, json_response, distance_json_response, radius, nw_coords, ne_coords, sw_coords, se_coords)

    # Prepare the JSON response
    json_data = []

    # Print the details of each result and add them to the JSON response
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

            result_data = {
                "name": name,
                "street_address": address,
                "street_name": street_name,
                "latitude": lat,
                "longitude": lng,
                "within_polygon": within_area
            }

            if not within_area:
                print(f"Distance to Polygon Edge: {blocks_to_edge:.2f} blocks")
                print(f"Direction to Nearest Edge: {direction_to_edge}")
                print("Nearest Edge Address:", nearest_edge_address)
                print("Nearest Edge Street Name:", nearest_edge_street_name)
                result_data["distance_to_edge"] = blocks_to_edge
                result_data["direction_to_edge"] = direction_to_edge
                result_data["nearest_edge_address"] = nearest_edge_address
                result_data["nearest_edge_street_name"] = nearest_edge_street_name

            print()
            json_data.append(result_data)
    else:
        print("No results found within Columbus, GA and within the specified radius.")

    # Print the total number of results
    total_results = len(result_details)
    print("Total results within Columbus, GA and within the specified radius:", total_results)
    print(get_nearby_businesses(lat, lng))
    print()

    # Return the JSON response
    return JsonResponse({"results": json_data, "total_results": total_results})

def convert_pluscode(pluscode):
    # Set up the MAPS API request parameters
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
   
    params = {
        'address': pluscode,        
        'key': MAPS_API_KEY
    }
    headers = {
        'Accept': 'application/json'
    }

    # Make the MAPS API request
    response = requests.request("GET", base_url, headers=headers, params=params)

    # Check the response status code
    if response.status_code == 200:
        # Request successful
        data = response.json()

        if data["status"] == "OK":
            result = data["results"][0]
            formatted_address = result["formatted_address"]
            latitude = result["geometry"]["location"]["lat"]
            longitude = result["geometry"]["location"]["lng"]

            return {
                "address": formatted_address,
                "latitude": latitude,
                "longitude": longitude
            }
        else:
            # Geocoding request failed
            return None        
    else:
        # Request failed
        return None
    
def get_nearby_businesses(latitude, longitude, radius=250, keyword='restaurant'):
    # Set up the Places API request parameters
    base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        'location': f"{latitude},{longitude}",
        'radius': radius,
        'key': MAPS_API_KEY
    }
    if keyword:
        params['keyword'] = keyword

    # Make the Places API request
    response = requests.request("GET", base_url, params=params)

    # Check the response status code
    if response.status_code == 200:
        # Request successful
        data = response.json()

        if data["status"] == "OK":
            businesses = []
            for result in data["results"]:
                # business = {
                #     "name": result["name"],
                #     "address": result.get("vicinity", ""),
                #     "latitude": result["geometry"]["location"]["lat"],
                #     "longitude": result["geometry"]["location"]["lng"]
                # }

                business_lat = result["geometry"]["location"]["lat"]
                business_lng = result["geometry"]["location"]["lng"]
                business_point = Point(business_lat, business_lng)

                is_within, distance, nearest_edge = is_within_area(business_point)

                if is_within:
                    business = {
                        "name": result["name"],
                        "address": result.get("vicinity", ""),
                        "latitude": business_lat,
                        "longitude": business_lng
                    }
                    businesses.append(business)
            return businesses
        else:
            # Places API request failed
            return None
    else:
        # Request failed
        return None


# CLASS BASED VIEWS   
class demoPageView(TemplateView):
    template_name = 'metra/demo.html'


    

