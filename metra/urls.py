from django.urls import path
from .views import (    
    search_places,
    demoPageView,  
)

app_name = 'metra'  # Declaring the namespace for this URLs module

urlpatterns = [ 
    path("", search_places, name="search_places"),
    path("demo/", demoPageView.as_view(), name="demo_page_view"),     
]