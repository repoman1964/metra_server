
from datetime import datetime, timezone
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from environs import Env
from geopy.distance import geodesic, distance
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
import json
import math
import pytz
import requests
import xml.etree.ElementTree as ET


from google_apis.views import (
    query_google_places_by_name, 
    query_google_places_by_address,
    query_google_places_by_place_id,)


# Load environment variables
env = Env()
env.read_env()
MAPS_API_KEY = env.str("MAPS_API_KEY")

# Coordinates of closest intersections
intersections = {
    "14th/1st": (32.47242130413214, -84.99173792408702),
    "14th/Broadway": (32.472445422278724, -84.99320734011852),
    "14th/Front": (32.4724695404136, -84.99458527520393),
    "13th/Front": (32.47054971621819, -84.99459099276146),
    "12th/Front": (32.46865249199726, -84.99467061753548),
    "12th/Bay": (32.46856324424755, -84.99543930851708),
    "11th/Bay": (32.466778270648305, -84.9958483367518),
    "10th/Bay": (32.46483855922165, -84.99598232882443),
    "10th/Front": (32.46485045940487, -84.99467061760059),
    "9th/Front": (32.462928557149944, -84.99467061763052),
    "9th/Broadway": (32.462910706472506, -84.99326017546244),
    "9th/1st": (32.462880955335606, -84.99178626339678),
    "10th/1st": (32.464820708893065, -84.99182152445096),
    "11th/1st": (32.466706870945146, -84.99177921111706),
    "12th/1st": (32.46864059229318, -84.99173689773896),
    "13th/1st": (32.47053262406687, -84.99175805435577)
}

@csrf_exempt
def getCurrentTime(request):    #set for EST
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)

        # Extract the toolCalls id
        tool_calls_id = data['message']['toolCalls'][0]['id'] 


        # Get server timestamp
        current_utc = datetime.now(timezone.utc)

        # Convert to local time
        # Columbus GA timezone conversion
        columbusTZ = pytz.timezone("America/New_York")
        current_local_time = datetime.now(columbusTZ)

        response_data = {
            "results": [
                {
                "toolCallId": tool_calls_id,
                "result": [
                    {
                        "current_utc": current_utc,
                        "current_local_time": current_local_time
                     }
                    ]
                }
            ]
        }      

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)


@csrf_exempt
def getCurrentWeather(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)
        print(data)

        # Extract the toolCalls id
        tool_calls_id = data['message']['toolCalls'][0]['id']
        location = data['message']['toolCalls'][0]['function']['arguments']['location']
        result = f"The current weather in {location} is 69°C, partly cloudy."
       

        response_data = {
            "results": [
                {
                "toolCallId": tool_calls_id,
                "result": result
                }
            ]
        }

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)   
    
@csrf_exempt
def getCurrentUTC(request):
    """
        Returns the current UTC timestamp.
        
        Returns:
            str: The current UTC timestamp in ISO 8601 format.
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)

        # Get server timestamp
        current_utc = datetime.now(timezone.utc)        

        # Extract the toolCalls id
        tool_calls_id = data['message']['toolCalls'][0]['id']     
       
        response_data = {
            "results": [
                {
                "toolCallId": tool_calls_id,
                "result": current_utc
                }
            ]
        }      

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
@csrf_exempt 
def getCurrentDayOfWeek(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
     
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)

        # Extract the toolCalls id
        tool_calls_id = data['message']['toolCalls'][0]['id'] 


        # Get server timestamp
        current_utc = datetime.now(timezone.utc)

        # Convert to local time
        # Columbus GA timezone conversion
        columbusTZ = pytz.timezone("America/New_York")
        current_local_time = datetime.now(columbusTZ)    

        # Get the day of the week
        day_of_week = current_local_time.strftime("%A")

        response_data = {
            "results": [
                {
                "toolCallId": tool_calls_id,
                "result": [
                    {
                        "day_of_week": day_of_week,
                     }
                    ]
                }
            ]
        }      


        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)


@csrf_exempt
def getPickupPointName(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)
        print(data)

        # Navigate through the nested dictionary structure to access the point_name
        pickup_point_name = (
            data.get('message', {})
                .get('functionCall', {})
                .get('parameters', {})
                .get('pickupPointName')
        )

        caller_phone_number = (
            data.get('message', {})
                .get('call', {})
                .get('customer', {})
                .get('number')
        )


        if not pickup_point_name:
            return JsonResponse({'error': 'pickupPointName not provided'}, status=400)
        
        # Query Google Places API with the point_name
        places_response_name = query_google_places_by_name(pickup_point_name)

        if places_response_name is None or 'results' not in places_response_name:
            return JsonResponse({'error': 'Failed to fetch places data'}, status=500)
        
        inside_service_area = []

        for place in places_response_name['results']:
            lat = place["geometry"]["location"]["lat"]
            lng = place["geometry"]["location"]["lng"]
            if is_in_service_area(lat, lng):
                inside_service_area.append({
                    'in_area': 'true',
                    'name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'latitude': lat,
                    'longitude': lng
                })
                print(f"Location ({lat}, {lng}) is inside the service area.")
            else:
                inside_service_area.append({
                    'in_area': 'false',                    
                    'locationLAT': lat,
                    'locationLNG': lng
                })
                print(f"Location ({lat}, {lng}) is outside the service area.")

        print(inside_service_area)

        response_data = {
            'message': 'Data received successfully',           
            'inside_service_area': inside_service_area,
            # 'caller_phone_number': format_phone_number(caller_phone_number)
            'caller_phone_number': caller_phone_number
        }

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

@csrf_exempt
def getDropOffPointName(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)
        print(data)

        # Navigate through the nested dictionary structure to access the point_name
        dropoff_point_name = (
            data.get('message', {})
                .get('functionCall', {})
                .get('parameters', {})
                .get('dropOffPointName')
        )

        caller_phone_number = (
            data.get('message', {})
                .get('call', {})
                .get('customer', {})
                .get('number')
        )


        if not dropoff_point_name:
            return JsonResponse({'error': 'dropOffPointName not provided'}, status=400)
        
        # Query Google Places API with the point_name
        places_response_name = query_google_places_by_name(dropoff_point_name)

        if places_response_name is None or 'results' not in places_response_name:
            return JsonResponse({'error': 'Failed to fetch places data'}, status=500)
        
        inside_service_area = []

        for place in places_response_name['results']:
            lat = place["geometry"]["location"]["lat"]
            lng = place["geometry"]["location"]["lng"]
            if is_in_service_area(lat, lng):
                inside_service_area.append({
                    'name': place.get('name'),
                    'address': place.get('formatted_address'),
                    'latitude': lat,
                    'longitude': lng
                })
                print(f"Location ({lat}, {lng}) is inside the service area.")
            else:
                print(f"Location ({lat}, {lng}) is outside the service area.")

        print(inside_service_area)

        response_data = {
            'message': 'Data received successfully',           
            'inside_service_area': inside_service_area,
            'caller_phone_number': format_phone_number(caller_phone_number)
        }

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
@csrf_exempt
def getPickupPointAddress(request):
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)
        # print(data)

        # Navigate through the nested dictionary structure to access the pickup_point_address
        pickup_point_address = (
            data.get('message', {})
                .get('functionCall', {})
                .get('parameters', {})
                .get('pickupPointAddress')
        )

        if not pickup_point_address:
            return JsonResponse({'error': 'getPickupPointAddress not provided'}, status=400)
        
        # Query Google Places API with the point_address
        places_response_address = query_google_places_by_address(pickup_point_address)
        print(places_response_address)        
        
        # Extract place_id from the places_response_address
        place_id = places_response_address.get('candidates', [{}])[0].get('place_id')
        if not place_id:
            return JsonResponse({'error': 'place_id not found in places response'}, status=500)
        
        # Query Google Places API with the place_id
        place_id_details = query_google_places_by_place_id(place_id)

        if not place_id_details:
            return JsonResponse({'error': 'Failed to fetch place id details'}, status=500)
        
        # Extract the latitude and longitude values
        lat = place_id_details['result']['geometry']['location']['lat']
        lng = place_id_details['result']['geometry']['location']['lng']
        if lat is not None and lng is not None:

            print(f"{lat}, {lng}")
            inside_service_area = []

            if is_in_service_area(lat, lng):
                # Find the street name in the address components
                for component in place_id_details['result']['address_components']:
                    if 'route' in component['types']:
                        street_name = component['long_name']
                        break

                inside_service_area.append({
                        'name': place_id_details['result']['name'],
                        'address': place_id_details['result']['formatted_address'],
                        'street_name': street_name,
                        'latitude': lat,
                        'longitude': lng
                    })
                
            print(inside_service_area)

            response_data = {
                'message': 'Data received successfully',           
                'inside_service_area': inside_service_area,
            }

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
@csrf_exempt
def getDropOffPointAddress(request):
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)
        # print(data)

        # Navigate through the nested dictionary structure to access the drop_off_point_address
        drop_off_point_address = (
            data.get('message', {})
                .get('functionCall', {})
                .get('parameters', {})
                .get('dropOffPointAddress')
        )

        if not drop_off_point_address:
            return JsonResponse({'error': 'getDropOffPointAddress not provided'}, status=400)
        
        # Query Google Places API with the point_name
        places_response_address = query_google_places_by_address(drop_off_point_address)
        print(places_response_address)

        # Extract place_id from the places_response_address
        place_id = places_response_address.get('candidates', [{}])[0].get('place_id')
        if not place_id:
            return JsonResponse({'error': 'place_id not found in places response'}, status=500)
        
        # Query Google Places API with the place_id
        place_id_details = query_google_places_by_place_id(place_id)
        if not place_id_details:
            return JsonResponse({'error': 'Failed to fetch place details'}, status=500)
        
        # Extract the latitude and longitude values
        lat = place_id_details['result']['geometry']['location']['lat']
        lng = place_id_details['result']['geometry']['location']['lng']
        if lat is not None and lng is not None:

            print(f"{lat}, {lng}")
            inside_service_area = []

            if is_in_service_area(lat, lng):
                # Find the street name in the address components
                for component in place_id_details['result']['address_components']:
                    if 'route' in component['types']:
                        street_name = component['long_name']
                        break

                inside_service_area.append({
                        'name': place_id_details['result']['name'],
                        'address': place_id_details['result']['formatted_address'],
                        'street_name': street_name,
                        'latitude': lat,
                        'longitude': lng
                    })
                
            print(inside_service_area)

            response_data = {
                'message': 'Data received successfully',           
                'inside_service_area': inside_service_area,
            }

        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)  

def is_in_service_area(lat, lng):
    """
    Check if a given latitude and longitude is inside the service area polygon.

    Args:
    - lat (float): Latitude of the point.
    - lng (float): Longitude of the point.

    Returns:
    - bool: True if the point is inside the polygon, False otherwise.
    """
    service_area_polygon = get_service_area_polygon()
    point = Point(lat, lng)
    return service_area_polygon.contains(point)



def get_service_area_polygon():
    tree = ET.parse('service area.kml')
    root = tree.getroot()

    # Extract coordinates (adjust the namespace if necessary)
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    coordinates = root.find('.//kml:coordinates', namespace).text.strip()

    # Split the coordinates string into a list of (longitude, latitude) tuples
    # NOTE: google delivers kml download as (lng, lat) format
    # shapely polygon requires (lat, lng) format
    coords = []
    for coord in coordinates.split():
        lng, lat, _ = map(float, coord.split(','))
        coords.append((lat, lng))

    # Use the extracted coordinates to create a Shapely polygon
    service_area_polygon = Polygon(coords)
    return service_area_polygon

def is_in_service_area(lat, lng):
    """
    Check if a given latitude and longitude is inside the service area polygon.

    Args:
    - lat (float): Latitude of the point.
    - lng (float): Longitude of the point.

    Returns:
    - bool: True if the point is inside the polygon, False otherwise.
    """
    service_area_polygon = get_service_area_polygon()
    point = Point(lat, lng)
    return service_area_polygon.contains(point)

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

@csrf_exempt
def getClosestIntersection(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    
    if not data:
        return JsonResponse({'error': 'Failed to fetch POST data'}, status=500)
    
    locationLAT = float(data['message']['functionCall']['parameters']['locationLAT'])
    locationLNG = float(data['message']['functionCall']['parameters']['locationLNG'])
    location_type = data['message']['functionCall']['parameters']['locationTYPE']
    origin = (locationLAT, locationLNG)

    closest_intersection, city_blocks, direction = find_intersection_based_on_type(origin, intersections, location_type)

    response_data = {
        'location_type': location_type,
        'closest_intersection': closest_intersection,
        'direction': direction,
        'distance_in_blocks': city_blocks,
    }

    return JsonResponse(response_data, status=200)    
   
def get_direction_and_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    
    if abs(lat_diff) > abs(lon_diff):
        return "north" if lat_diff > 0 else "south"
    else:
        return "east" if lon_diff > 0 else "west" 

def find_intersection_based_on_type(origin, intersections, location_type):
    closest_intersection = None
    min_distance = float('inf')
    max_distance = float('-inf')
    target_intersection = None

    for name, coords in intersections.items():
        dist = geodesic(origin, coords).miles
        if location_type == 'pickup' and dist < min_distance:
            min_distance = dist
            closest_intersection = name
        elif location_type == 'dropoff' and dist > max_distance:
            max_distance = dist
            target_intersection = name

    if location_type == 'pickup':
        final_intersection = closest_intersection
        final_distance = min_distance
    else:
        final_intersection = target_intersection
        final_distance = max_distance

    direction = get_direction_and_distance(origin, intersections[final_intersection])
    
    # Assuming 1 mile = 20 city blocks (adjust as necessary)
    if "east" in direction or "west" in direction:
        city_blocks = round(final_distance * 20 / 1.5)  # Assuming 1.5 blocks per 0.1 miles
    else:
        city_blocks = round(final_distance * 20 / 2.5)  # Assuming 2.5 blocks per 0.1 miles
    
    return final_intersection, city_blocks, direction

def find_closest_intersection(origin, intersections):
    closest_intersection = None
    min_distance = float('inf')
    for name, coords in intersections.items():
        dist = distance(origin, coords).miles
        if dist < min_distance:
            min_distance = dist
            closest_intersection = name

    direction = get_direction_and_distance(origin, intersections[closest_intersection])
    # Assuming 1 mile = 20 city blocks (this is an approximate value, adjust if needed)

    if "east" in direction or "west" in direction:
        city_blocks = round(min_distance * 12)
    else:
        city_blocks = round(min_distance * 8)
    
    
    return closest_intersection, city_blocks, direction   



    

 

