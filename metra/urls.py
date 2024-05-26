from django.urls import path


from .views import (    
    demoPageView,  
)

from google_apis.views import query_google_places_by_name

app_name = 'metra'  # Declaring the namespace for this URLs module

urlpatterns = [ 
    path("", query_google_places_by_name, name="query_places_api"),
    path("demo/", demoPageView.as_view(), name="demo_page_view"),     
]