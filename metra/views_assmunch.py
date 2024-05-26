from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic
import math

# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# def check_point_within_service_area(request):

#     # Set up the Places API request parameters
#     BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
#     query = "sharks"
#     query = "2WR"
#     location = "32.463307,-84.993284"  # Latitude and longitude of the reference point (shuttle garage)
#     radius = 30000  # Radius in meters (3 km)
#     params = {
#         'query': query,
#         'location': location,
#         'radius': radius,
#         'key': MAPS_API_KEY
#     }
#     headers = {
#         'Accept': 'application/json'
#     }

#     # Make the Places API request
#     response = requests.request("GET", base_url, headers=headers, params=params)

#     # Get the JSON response from the Places API
#     json_response = response.text

# def miles_to_city_blocks(miles, block_length=350):
#     feet_per_mile = 5280
#     blocks_per_mile = feet_per_mile / block_length
#     return miles * blocks_per_mile

# def calculate_direction(point, nearest_edge_coords):
#     delta_y = nearest_edge_coords[0] - point[0]
#     delta_x = nearest_edge_coords[1] - point[1]
#     angle = math.atan2(delta_y, delta_x)
#     degrees = math.degrees(angle)
    
#     if degrees < 0:
#         degrees += 360
    
#     if 45 <= degrees < 135:
#         return "East"
#     elif 135 <= degrees < 225:
#         return "South"
#     elif 225 <= degrees < 315:
#         return "West"
#     else:
#         return "North"

# def is_within_area(point, nw_coords, ne_coords, sw_coords, se_coords):
#     # Define the points
#     point = Point(point)
#     nw_point = Point(nw_coords)
#     ne_point = Point(ne_coords)
#     sw_point = Point(sw_coords)
#     se_point = Point(se_coords)

#     # Define the polygon
#     polygon = Polygon([nw_point, ne_point, se_point, sw_point, nw_point])

#     # Check if the point is within the polygon
#     if polygon.contains(point):
#         return True, 0.0, None

#     # Calculate the nearest distance to the polygon edges
#     # Find the nearest point on the polygon to the point
#     nearest_point = nearest_points(point, polygon.boundary)[1]
#     nearest_edge_coords = (nearest_point.y, nearest_point.x)

#     # Calculate the geodesic distance between the points in miles
#     distance = geodesic((point.y, point.x), (nearest_point.y, nearest_point.x)).miles

#     return False, distance, nearest_edge_coords

# @csrf_exempt
# def get_result_details(request):
#     if request.method == 'GET':
#         json_data = request.GET.get('json_data')
#         distance_data = request.GET.get('distance_data')
#         radius = int(request.GET.get('radius'))
#         nw_coords = tuple(map(float, request.GET.get('nw_coords').split(',')))
#         ne_coords = tuple(map(float, request.GET.get('ne_coords').split(',')))
#         sw_coords = tuple(map(float, request.GET.get('sw_coords').split(',')))
#         se_coords = tuple(map(float, request.GET.get('se_coords').split(',')))
#         query = request.GET.get('query')

#         # Parse the JSON data
#         data = json.loads(json_data)
#         distances = json.loads(distance_data)

#         # Check if the status is "OK"
#         if data['status'] == 'OK' and distances['status'] == 'OK':
#             results = data['results']
#             result_details = []
#             for i, result in enumerate(results):
#                 name = result['name']
#                 lat = result['geometry']['location']['lat']
#                 lng = result['geometry']['location']['lng']
#                 distance = distances['rows'][0]['elements'][i]['distance']['value']  # Get distance in meters

#                 # Check if the result is within Columbus, GA, contains the query term in the name, and is within the specified radius
#                 if 'Columbus' in result['formatted_address'] and 'GA' in result['formatted_address'] and query.lower() in name.lower() and distance <= radius:
#                     city = 'Columbus'
#                     state = 'GA'
                    
#                     # Retrieve the street address using the Geocoding API
#                     geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={MAPS_API_KEY}"
#                     geocode_response = requests.get(geocode_url)
#                     geocode_data = json.loads(geocode_response.text)
                    
#                     if geocode_data['status'] == 'OK' and len(geocode_data['results']) > 0:
#                         street_address = geocode_data['results'][0]['formatted_address']
#                         street_name = next((component['long_name'] for component in geocode_data['results'][0]['address_components'] if 'route' in component['types']), 'N/A')
#                     else:
#                         street_address = 'N/A'
#                         street_name = 'N/A'
                    
#                     # Check if the location is within the defined polygon
#                     within_area, distance_to_edge, nearest_edge_coords = is_within_area((lat, lng), nw_coords, ne_coords, sw_coords, se_coords)

#                     if not within_area:
#                         # Convert the distance to city blocks
#                         blocks_to_edge = miles_to_city_blocks(distance_to_edge)

#                         # Calculate the general direction to the nearest edge point
#                         direction_to_edge = calculate_direction((lat, lng), nearest_edge_coords)
                        
#                         # Retrieve the human-readable address of the nearest edge
#                         nearest_edge_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={nearest_edge_coords[0]},{nearest_edge_coords[1]}&key={MAPS_API_KEY}"
#                         nearest_edge_response = requests.get(nearest_edge_url)
#                         nearest_edge_data = json.loads(nearest_edge_response.text)
                        
#                         if nearest_edge_data['status'] == 'OK' and len(nearest_edge_data['results']) > 0:
#                             nearest_edge_address = nearest_edge_data['results'][0]['formatted_address']
#                             nearest_edge_street_name = next((component['long_name'] for component in nearest_edge_data['results'][0]['address_components'] if 'route' in component['types']), 'N/A')
#                         else:
#                             nearest_edge_address = 'N/A'
#                             nearest_edge_street_name = 'N/A'
#                     else:
#                         nearest_edge_address = 'N/A'
#                         nearest_edge_street_name = 'N/A'
#                         blocks_to_edge = 0
#                         direction_to_edge = 'N/A'
                    
#                     result_details.append({
#                         'name': name,
#                         'lat': lat,
#                         'lng': lng,
#                         'street_address': street_address,
#                         'street_name': street_name,
#                         'within_area': within_area,
#                         'distance_to_edge': distance_to_edge,
#                         'blocks_to_edge': blocks_to_edge,
#                         'direction_to_edge': direction_to_edge,
#                         'nearest_edge_address': nearest_edge_address,
#                         'nearest_edge_street_name': nearest_edge_street_name
#                     })

#             # Sort the result_details list based on the distance (ascending order)
#             result_details.sort(key=lambda x: x['distance_to_edge'])

#             return JsonResponse({'result_details': result_details, 'total_results': len(result_details)})
#         else:
#             return JsonResponse({'result_details': [], 'total_results': 0})

def search_location(request):
    if request.method == 'POST' or 'GET': #for development, VAPI sends a POST request

        # Set up the Places API request parameters
        BASE_URL_NAME_SEARCH = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        query = "sharks"
        query = "2WR"
        location = "32.463307,-84.993284"  # Latitude and longitude of the reference point (shuttle garage)
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
        data = response.text



       
        # # Perform a text-based search using Google Maps API
        # api_key = 'MAPS_API_KEY'
        # url = f'https://maps.googleapis.com/maps/api/geocode/json?address={origin}&key={api_key}'
        # response = requests.get(url)
        # data = response.json()
        
        if data['status'] == 'OK':
            result = data['results'][0]
            location = result['geometry']['location']
            lat, lng = location['lat'], location['lng']
            
            # Check if the location is in Columbus, GA
            columbus_ga = False
            for component in result['address_components']:
                if 'locality' in component['types'] and component['long_name'] == 'Columbus':
                    if 'administrative_area_level_1' in component['types'] and component['short_name'] == 'GA':
                        columbus_ga = True
                        break
            
            # Define the polygon coordinates
            nw_coords = (32.47361181679043, -84.99502757805325)
            ne_coords = (32.474305395776845, -84.99039374856852)
            sw_coords = (32.461455254991144, -84.99640233868355)
            se_coords = (32.46287557552805, -84.99040377675384)
            
            # Create a Shapely polygon
            polygon = Polygon([nw_coords, ne_coords, se_coords, sw_coords])
            
            # Check if the location is within the polygon
            point = Point(lat, lng)
            inside_polygon = polygon.contains(point)
            
            if not inside_polygon:
                # Calculate the distance and cardinal direction to the closest edge
                distance = polygon.exterior.distance(point)
                closest_point = polygon.exterior.interpolate(polygon.exterior.project(point))
                closest_lat, closest_lng = closest_point.y, closest_point.x
                
                # Get the actual address of the closest edge
                url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={closest_lat},{closest_lng}&key={api_key}'
                response = requests.get(url)
                data = response.json()
                
                if data['status'] == 'OK':
                    closest_address = data['results'][0]['formatted_address']
                else:
                    closest_address = 'Address not found'
                
                # Find well-known landmarks or other references near the closest edge
                url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={closest_lat},{closest_lng}&radius=500&key={api_key}'
                response = requests.get(url)
                data = response.json()
                
                if data['status'] == 'OK':
                    landmarks = [place['name'] for place in data['results']]
                else:
                    landmarks = []
                
                # Determine the cardinal direction
                if closest_lat > lat:
                    direction = 'North'
                elif closest_lat < lat:
                    direction = 'South'
                else:
                    direction = 'East' if closest_lng > lng else 'West'
                
                return JsonResponse({
                    'location': result['formatted_address'],
                    'lat': lat,
                    'lng': lng,
                    'columbus_ga': columbus_ga,
                    'inside_polygon': inside_polygon,
                    'distance': distance,
                    'direction': direction,
                    'closest_edge': {
                        'lat': closest_lat,
                        'lng': closest_lng,
                        'address': closest_address,
                        'landmarks': landmarks
                    }
                })
            
            return JsonResponse({
                'location': result['formatted_address'],
                'lat': lat,
                'lng': lng,
                'columbus_ga': columbus_ga,
                'inside_polygon': inside_polygon
            })
        
        return JsonResponse({'error': 'Location not found'})
    
    return JsonResponse({'error': 'Invalid request method'})