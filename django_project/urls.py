from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from vapi.views import (    
    getCurrentTime,  
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vapi/", include("vapi.urls")),
    path("metra/", include("metra.urls")),
    path("", getCurrentTime, name="getCurrentTime"), 
    path("assistant/", include("assistant.urls")),
   ]
