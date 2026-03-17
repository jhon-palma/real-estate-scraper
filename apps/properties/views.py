from django.shortcuts import render

from apps.properties.models import Property

def properties_list(request):
    properties = Property.objects.all()

    return render(request,"properties/list.html",{"properties": properties})


def property_detail(request, id):
    property = Property.objects.prefetch_related("images").get(id=id)

    return render(request,"properties/detail.html",{"property": property})

