from django.core.management.base import BaseCommand

from apps.scraper.services.remax_ec import RemaxScraper
from apps.properties.models import Property, PropertyImage


class Command(BaseCommand):

    def add_arguments(self, parser):

        parser.add_argument(
            "--limit",
            type=int,
            help="Limite de propiedades a scrapear"
        )

    def handle(self, *args, **options):
        scraper = RemaxScraper()

        limit = options.get("limit")

        qs = Property.objects.filter(
            source="remax_ec",
            scraped=False
        )

        if limit:
            qs = qs[:limit]
            
        print("TOTAL:", qs.count())

        for prop in qs:

            print("DETAIL:", prop.url)

            try:

                data = scraper.get_detail(prop.url)

            except Exception as e:

                print("ERROR", e)
                continue

            if not data:
                continue

            code = data["code"]

            if code:

                existing = Property.objects.filter(
                    source="remax_ec",
                    external_code=code
                ).exclude(id=prop.id).first()

                if existing:

                    print("DUPLICATE", code)

                    prop.delete()

                    continue

            prop.external_code = data["code"]
            prop.title = data["title"]
            prop.price = data["price"]
            prop.agent = data["agent"]

            prop.total_area = data["total_area"]
            prop.covered_area = data["covered_area"]
            prop.semi_covered_area = data["semi_covered_area"]
            prop.land_area = data["land_area"]

            prop.rooms = data["rooms"]
            prop.bedrooms = data["bedrooms"]
            prop.description = data["description"]
            prop.bathrooms = data["bathrooms"]
            prop.half_bathrooms = data["half_bathrooms"]
            prop.parking = data["parking"]
            prop.antiquity = data["antiquity"]
            prop.property_floors = data["property_floors"]
            prop.expenses  = data["expenses"]
            prop.location = data["location"]
            prop.latitude = data["lat"]
            prop.longitude = data["lng"]
            prop.suitable_credit = data["suitable_credit"]
            prop.offer_financing = data["offer_financing"]
            prop.suitable_professional = data["suitable_professional"]
            prop.extras = data["extras"]
            prop.office_name = data["office_name"]
            prop.office_address = data["office_address"]
            prop.office_image = data["office_image"]

            prop.scraped = True

            prop.save()

            for img in data["images"]:

                PropertyImage.objects.get_or_create(
                    property=prop,
                    url=img
                )