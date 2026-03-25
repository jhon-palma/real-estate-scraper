from django.db import models
import uuid

class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    OPERATION_CHOICES = [
        ("sale", "Venta"),
        ("rent", "Renta"),
    ]
    source = models.CharField(max_length=50, db_index=True)
    url = models.URLField(null=True, blank=True, db_index=True)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    title = models.CharField(max_length=500, null=True, blank=True)
    subtitle = models.CharField(max_length=500, null=True, blank=True)
    external_code = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    description = models.TextField(null=True, blank=True)
    agent = models.CharField(max_length=200, null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    currency = models.CharField(max_length=5, null=True, blank=True)
    total_area = models.FloatField(null=True, blank=True, verbose_name="Superficie total")
    covered_area = models.FloatField(null=True, blank=True, verbose_name="Superficie cubierta")
    semi_covered_area = models.FloatField(null=True, blank=True, verbose_name="Superficie semicubierta")
    land_area = models.FloatField(null=True, blank=True, verbose_name="Superficie terreno")
    land = models.CharField(max_length=20, null=True, blank=True, verbose_name="Terreno")
    rooms = models.IntegerField(null=True, blank=True, verbose_name="Ambientes")
    room_details = models.JSONField(null=True, blank=True)
    land_use = models.CharField(max_length=200, null=True, blank=True)
    bedrooms = models.IntegerField(null=True, blank=True, verbose_name="Dormitorios")
    bathrooms = models.IntegerField(null=True, blank=True, verbose_name="Baños")
    half_bathrooms = models.IntegerField(null=True, blank=True, verbose_name="Medios Baños")
    parking = models.IntegerField(null=True, blank=True, verbose_name="Parqueaderos")
    antiquity = models.IntegerField(null=True, blank=True, verbose_name="Antigüedad")
    year = models.CharField(max_length=10, null=True, blank=True, verbose_name="Año/mes de construccion")
    suitable_credit = models.BooleanField(null=True, blank=True, verbose_name="Apto crédito")
    offer_financing = models.BooleanField(null=True, blank=True, verbose_name="Ofrece financiamiento")
    suitable_professional = models.BooleanField(null=True, blank=True, verbose_name="Apto profesional")
    price_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Tipo de precio")
    property_floors = models.IntegerField(null=True, blank=True, verbose_name="Pisos de la propiedad")
    additional_costs = models.CharField(max_length=5, null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    expenses = models.CharField(max_length=200, null=True, blank=True, verbose_name="Expensas")
    location = models.TextField(null=True, blank=True, verbose_name="Ubicación")
    extras = models.JSONField(null=True, blank=True)
    office_name = models.CharField(max_length=255, null=True, blank=True)
    office_address = models.TextField(null=True, blank=True)
    office_image = models.URLField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    scraped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "external_code"],
                name="unique_source_external_code",
                condition=~models.Q(external_code=None),
            )
        ]

class PropertyImage(models.Model):

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images"
    )

    url = models.URLField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )
