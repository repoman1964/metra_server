from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic

def is_within_area(hotel_indigo, nw_coords, ne_coords, sw_coords, se_coords):
    # Define the points
    dunkin_donuts = Point(hotel_indigo)
    nw_point = Point(nw_coords)
    ne_point = Point(ne_coords)
    sw_point = Point(sw_coords)
    se_point = Point(se_coords)

    # Define the polygon
    polygon = Polygon([nw_point, ne_point, se_point, sw_point, nw_point])

    # Check if dunkin_donuts is within the polygon
    if polygon.contains(dunkin_donuts):
        return True, 0.0

    # Calculate the nearest distance to the polygon edges
    # Find the nearest point on the polygon to the dunkin_donuts
    nearest_point = nearest_points(dunkin_donuts, polygon.boundary)[1]

    # Calculate the geodesic distance between the points in miles
    distance = geodesic((dunkin_donuts.y, dunkin_donuts.x), (nearest_point.y, nearest_point.x)).miles

    return False, distance

# Coordinates from the file
origin = (32.532270, -84.956660)
hotel_indigo = (32.472481, -84.993042)
nw_coords = (32.472546064404, -84.99463382471089)
ne_coords = (32.47244649932993, -84.99186578507934)
sw_coords = (32.46105423026278, -84.99638061912495)
se_coords = (32.46290893943292, -84.99041537310289)


# Check if hotel_indigo is within the area and get the distance if not
within_area, distance = is_within_area(hotel_indigo, nw_coords, ne_coords, sw_coords, se_coords)

if within_area:
    print("hotel_indigo is within the defined area.")
else:
    print(f"hotel_indigo is not within the defined area. Distance to the nearest edge: {distance:.2f} miles.")
