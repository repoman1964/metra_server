from shapely.geometry import Point, Polygon

def point_distance_from_area():
    # Coordinates from the text file
    origin = (32.465940, -84.992720)
    flanders = (45.525890, -122.618360)
    nw_point = (32.472546064404, -84.99463382471089)
    ne_point = (32.47244649932993, -84.99186578507934)
    sw_point = (32.46105423026278, -84.99638061912495)
    se_point = (32.46290893943292, -84.99041537310289)
    
    # Create a Polygon using the four points
    area = Polygon([nw_point, ne_point, se_point, sw_point])
    
    # Create a Point for the origin
    origin_point = Point(origin)
    flanders_point = Point(flanders)

    # Check if the origin point is within the area
    is_within = area.contains(flanders_point)

    # Calculate the distance from the point to the polygon
    distance = flanders_point.distance(area) if not is_within else 0

    return is_within, distance
    
    # # Check if the origin point is within the area
    # # return area.contains(origin_point)
    # return area.contains(flanders_point)

# # Call the function and print the result
# result = is_point_in_area()
# print("Is the origin point within the area?", result)

# Call the function and print the result
is_within, distance = point_distance_from_area()
if is_within:
    print("The origin point is within the area.")
else:
    print(f"The origin point is outside the area by {distance:.6f} units.")
