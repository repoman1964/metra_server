import xml.etree.ElementTree as ET
from shapely.geometry import Polygon

# Parse the KML file


tree = ET.parse('service area.kml')

# tree = ET.parse('/home/jose/Documents/MARION SYSTEMS/DIMENSION SEVEN SYSTEMS/PROJECTS/METRA INBOUND/server/service area.kml')
root = tree.getroot()

# Extract coordinates (adjust the namespace if necessary)
namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
coordinates = root.find('.//kml:coordinates', namespace).text.strip()

# Split the coordinates string into a list of (longitude, latitude) tuples
coords = []
for coord in coordinates.split():
    lon, lat, _ = map(float, coord.split(','))
    coords.append((lat, lon))

# Use the extracted coordinates to create a Shapely polygon
polygon = Polygon(coords)

# Print the polygon object
print(polygon)

# Print the area and the length of the polygon
print(f'Area: {polygon.area}')
print(f'Length: {polygon.length}')
