from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dateutil.parser import isoparse
from datetime import datetime
import pytz
from geopy.distance import distance

from django.utils import timezone
import datetime
import phonenumbers
import json

from google_apis.views import (
    query_google_places_by_name, 
    query_google_places_by_address,
    query_google_places_by_place_id,)

from metra.views import is_in_service_area   

# TIME FOCUSED

@csrf_exempt
def getCurrentUTC(request):
    current_utc = timezone.now().isoformat()
    # Return the current local time
    return JsonResponse({'current_utc_timestamp': current_utc})

def get_current_day(request):
    current_utc = getCurrentUTC(request)
    # Parse the UTC timestamp string into a datetime object
    utc_datetime = isoparse(current_utc)

    # Extract the day of the month
    day_of_month = utc_datetime.day
    return JsonResponse({'day_of_month': day_of_month})

def get_current_month(request):
    current_utc = getCurrentUTC(request)
    # Parse the UTC timestamp string into a datetime object
    utc_datetime = isoparse(current_utc)
    # Extract the month
    month = utc_datetime.month
    return JsonResponse({'month': month})

def get_current_year(request):
    current_utc = getCurrentUTC(request)
    # Parse the UTC timestamp string into a datetime object
    utc_datetime = isoparse(current_utc)

    # Extract the year
    year = utc_datetime.year
    return JsonResponse({'year': year})

@csrf_exempt
def getCurrentDayOfWeek(request):  
    
    # Get the current date
    current_date = datetime.datetime.now()

    # Define the Eastern Time timezone
    eastern_tz = pytz.timezone('US/Eastern')
    
    # Convert the UTC datetime to Eastern Time
    eastern_datetime = current_date.astimezone(eastern_tz)

    # Get the day of the week
    day_of_week = eastern_datetime.strftime("%A")

    # Return the corresponding day name
    return JsonResponse({'day_of_week': day_of_week})

@csrf_exempt
def getCurrentTime(request):    #set for EST
    eastern = pytz.timezone('US/Eastern')
    eastern_time = datetime.datetime.now(eastern)
    eastern_time = eastern_time.strftime('%-I:%M %p')
    
    # Return the current local time
    return JsonResponse({'eastern_time': eastern_time,
                         'current_time': eastern_time
                         })

@csrf_exempt
def getPickupPointName(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    try:
        # Assuming the POST data is sent as JSON
        data = json.loads(request.body)
        # print(data)

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
        # print(data)

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




def format_phone_number(phone_number, region='US'):
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_number, region)

        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            return "Invalid phone number"
        
        # Get the national format
        national_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)

        return {            
            "caller_phone_number": national_format,           
        }

    except phonenumbers.NumberParseException as e:
        return str(e)