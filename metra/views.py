import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic, distance
from django.http import JsonResponse
import math
import xml.etree.ElementTree as ET
from django.views.decorators.csrf import csrf_exempt


from django.views.generic import TemplateView

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
    
# CLASS BASED VIEWS   
class demoPageView(TemplateView):
    template_name = 'metra/demo.html'


    

