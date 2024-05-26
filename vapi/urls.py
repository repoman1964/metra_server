from django.urls import path
from metra.views import getClosestIntersection

from .views import (
    
    getCurrentUTC,
    getCurrentTime,
    getCurrentDayOfWeek,

    getPickupPointName,
    getPickupPointAddress,
    getDropOffPointName,
    getDropOffPointAddress,
    
)

app_name = 'vapi'  # Declaring the namespace for this URLs module

urlpatterns = [ 

    path('get-current-time/', getCurrentTime, name='get_current_time'),
    path("get-current-day-of-week/", getCurrentDayOfWeek, name="getCurrentDayOfWeek"),
    path("get-utc/", getCurrentUTC, name="getCurrentUTC"),

    path("get-pickup-point-name/", getPickupPointName, name="getPickupPointName"),
    path("get-pickup-point-address/", getPickupPointAddress, name="getPickupPointAddress"),

    path("get-dropoff-point-name/", getDropOffPointName, name="getDropOffPointName"),
    path("get-dropoff-point-address/", getDropOffPointAddress, name="getDropOffPointAddress"),

    path("get-closest-intersection/", getClosestIntersection, name="getClosestIntersection"),

    


    # path("month/", get_current_month, name="get_current_month"),
    # path("year/", get_current_year, name="get_current_year"),


     
]