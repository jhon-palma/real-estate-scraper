from django.core.management.base import BaseCommand

from apps.properties.models import Property
from apps.scraper.models import ScraperState
from apps.scraper.services.remax_cl import RemaxScraper



class Command(BaseCommand):

    help = "Scraper REMAX Chile"
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reiniciar scraping desde la página 1",
        )

    def handle(self, *args, **options):

        scraper = RemaxScraper()
        # items = scraper.get_list()
        # for item in items:
        #     url = item["url"]
        #     print("NEW", url)

        state, _ = ScraperState.objects.get_or_create(
            source="remax_cl",
            name='Remax Chile',
            url='https://www.remax.cl',
        )

        if options["reset"]:
            state.last_page = 1
            state.save()
            self.stdout.write(self.style.WARNING("RESET TO PAGE 1"))

        page = state.last_page

        print("START FROM PAGE:", page)

        while True:

            print("PAGE", page)

            try:

                items = scraper.get_list(page)
                print("========================")
                print(items)
                print("========================")
                print("========================")

            except Exception as e:

                print("ERROR PAGE", page, e)

                page += 1
                state.last_page = page
                state.save()

                continue

            if not items:
                print("NO MORE RESULTS")
                break
            
            for item in items:
                url = item["url"]
                external_code = item["external_code"]
                lng = item["lng"]
                lat = item["lat"]

                if not url:
                    continue

                obj, created = Property.objects.get_or_create(
                    url=url,
                    external_code=external_code,
                    
                    defaults={
                        "source": "remax_cl",
                        "operation": "sale",
                    }
                )

                obj.longitude = lng
                obj.latitude = lat
                obj.save()
                
                if created:
                    print("NEW", url)

            page += 1

            state.last_page = page
            state.save()