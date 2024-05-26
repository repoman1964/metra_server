from geopy.distance import distance
import math

# Coordinates of intersections
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

# Initial origin point
origin = (32.4717146, -84.9870967)
origin = (32.46004905798544, -84.99423143174792)

def get_direction_and_distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    lat_diff = lat2 - lat1
    lon_diff = lon2 - lon1
    
    if abs(lat_diff) > abs(lon_diff):
        return "north" if lat_diff > 0 else "south"
    else:
        return "east" if lon_diff > 0 else "west"

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

closest_intersection, city_blocks, direction = find_closest_intersection(origin, intersections)

print(f"Closest Intersection: {closest_intersection}")
print(f"Distance: {city_blocks} city blocks")
print(f"Direction: {direction}")
