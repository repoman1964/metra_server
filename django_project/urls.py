from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vapi/", include("vapi.urls")),
    path("metra/", include("metra.urls")),
   ]
