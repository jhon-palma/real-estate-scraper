from django.urls import path
from .views.scraper import *

urlpatterns = [

    path("scrapers/", scraper_list, name="scraper_list"),
    path("scrapers/<int:pk>/", scraper_detail, name="scraper_detail"),
    path("scrapers/<int:pk>/run/", scraper_run, name="scraper_run"),
    path("scrapers/<int:pk>/reset/", scraper_reset, name="scraper_reset"),
    # path("scraper/remax_ec/detail/", scraper_detail_run, name="scraper_detail_run"),
    path("scraper/<int:pk>/detail/run/", scraper_run_detail, name="scraper_run_detail"),

]