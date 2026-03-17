from django.urls import path
from .views import *

urlpatterns = [

    path("", properties_list, name="properties_list"),
    path("properties/<uuid:id>/", property_detail, name="property_detail"),

]