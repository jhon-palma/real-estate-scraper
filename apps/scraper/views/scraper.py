from django.shortcuts import render, get_object_or_404, redirect
from django.core.management import call_command
from django.contrib import messages

from apps.properties.models import Property
from apps.scraper.models import ScraperState


def scraper_list(request):
    scrapers = ScraperState.objects.all()

    return render(request,"scraper/list.html",{"scrapers": scrapers})


def scraper_detail(request, pk):

    scraper = get_object_or_404(ScraperState, pk=pk)

    total = Property.objects.filter(source=scraper.source ).count
    total_scraped = Property.objects.filter(source=scraper.source, scraped=True).count()
    total_pending = Property.objects.filter(source=scraper.source, scraped=False).count()

    return render(
        request,
        "scraper/detail.html",
        {
            "scraper": scraper,
            "total": total,
            "total_scraped": total_scraped,
            "total_pending": total_pending,
        }
    )

def scraper_run(request, pk):
    scraper = get_object_or_404(ScraperState,pk=pk)

    if scraper.source == "remax_ec":
        call_command("remax_ec")

    messages.success(request, "Scraper ejecutado")

    return redirect("scraper_detail",pk=pk)


def scraper_reset(request, pk):
    scraper = get_object_or_404(ScraperState, pk=pk)

    if scraper.source == "remax_ec":
        call_command("remax_ec", reset=True)

    messages.warning(request, "Scraper reiniciado")

    return redirect("scraper_detail", pk=pk)


def scraper_run_detail(request, pk):

    scraper = get_object_or_404(
        ScraperState,
        pk=pk
    )

    limit = request.POST.get("limit")

    if scraper.source == "remax_ec":

        if limit:
            call_command(
                "scrape_remax_ec_detail",
                limit=int(limit)
            )
        else:
            call_command(
                "scrape_remax_ec_detail"
            )

    messages.success(
        request,
        "Scraper detalle ejecutado"
    )

    return redirect(
        "scraper:scraper_detail",
        pk=pk
    )

# def scraper_detail_run(request):

#     if request.method == "POST":

#         limit = request.POST.get("limit")

#         if limit:
#             call_command(
#                 "remax_ec_detail",
#                 limit=int(limit)
#             )
#         else:
#             call_command(
#                 "remax_ec_detail"
#             )

#         messages.success(
#             request,
#             "Scraping ejecutado"
#         )

#         return redirect("scraper_detail_run")

#     return render(
#         request,
#         "scraper/run_detail.html"
#     )