from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from dateutil.parser import isoparse
from datetime import datetime
import pytz

from django.http import JsonResponse
from django.utils import timezone
import datetime

def get_current_utc(request):
    current_utc = timezone.now().isoformat()
    print(current_utc)
    return current_utc

def get_current_day(request):
    current_utc = get_current_utc(request)
    # Parse the UTC timestamp string into a datetime object
    utc_datetime = isoparse(current_utc)

    # Extract the day of the month
    day_of_month = utc_datetime.day
    print(day_of_month)
    return JsonResponse({'day_of_month': day_of_month})

def get_current_month(request):
    current_utc = get_current_utc(request)
    # Parse the UTC timestamp string into a datetime object
    utc_datetime = isoparse(current_utc)

    # Extract the month
    month = utc_datetime.month

    print(month)
    return JsonResponse({'month': month})

def get_current_year(request):
    current_utc = get_current_utc(request)
    # Parse the UTC timestamp string into a datetime object
    utc_datetime = isoparse(current_utc)

    # Extract the year
    year = utc_datetime.year

    print(year)
    return JsonResponse({'year': year})

@csrf_exempt
def get_day_of_week(request):  
    
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
def get_current_eastern_time(request):
    eastern = pytz.timezone('US/Eastern')
    eastern_time = datetime.datetime.now(eastern)
    eastern_time = eastern_time.strftime('%-I:%M %p')
    
    # Return the corresponding day name
    return JsonResponse({'eastern_time': eastern_time})