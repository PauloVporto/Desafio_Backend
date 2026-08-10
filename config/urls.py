from django.urls import path

from config.admin_site import admin_site

urlpatterns = [
    path("", admin_site.urls),
]
