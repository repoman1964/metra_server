import requests
import json
from environs import Env
from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
from geopy.distance import geodesic
import math

# Define the boundary points
boundary_points = {
    "nw": (32.47361181679043, -84.99502757805325),
    "ne": (32.474305395776845, -84.99039374856852),
    "sw": (32.461455254991144, -84.99640233868355),
    "se": (32.46287557552805, -84.99040377675384)
}
 
def is_within_area(point, boundary_points):
    """
    Check if a given point is within a polygon defined by the boundary points.

    Parameters:
    - point (tuple): The coordinates of the point to check.
    - boundary_points (dict): A dictionary containing the coordinates of the boundary points.
    
    Returns:
    - bool: True if the point is within the polygon, False otherwise.
    """
    # Convert the input point to a shapely Point
    point = Point(point)

    # Convert the boundary points to shapely Points and create the polygon
    polygon = Polygon([boundary_points["nw"], boundary_points["ne"], boundary_points["se"], boundary_points["sw"]])

    # Check if the point is within the polygon
    return polygon.contains(point)

# Example usage
point_to_check = (32.47384054176605, -84.9895034748196)
is_within = is_within_area(point_to_check, boundary_points)
print(f"The point {point_to_check} is within the area: {is_within}")