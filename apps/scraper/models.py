from django.db import models


class ScraperState(models.Model):
    source = models.CharField(max_length=50)
    last_page = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    
    def __str__(self):
        return f"{self.source} - {self.last_page}"
