from django.urls import path

from .views import (
    
    get_current_utc,
    get_current_eastern_time,
    get_current_day,
    get_current_month,
    get_current_year,

    get_day_of_week,
)

app_name = 'vapi'  # Declaring the namespace for this URLs module

urlpatterns = [ 

    path("utc/", get_current_utc, name="utc"), 
    
    path('time/', get_current_eastern_time, name='get_current_time'),
    path("day/", get_current_day, name="get_current_day"),
    path("month/", get_current_month, name="get_current_month"),
    path("year/", get_current_year, name="get_current_year"),

    path("day-of-week/", get_day_of_week, name="get_day_of_week"),

     
]