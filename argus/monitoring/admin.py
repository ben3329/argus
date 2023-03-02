from django.contrib import admin

# Register your models here.
from .models import Asset, Secret, ScrapingCode, Monitor

# Register your models here.
admin.site.register(Asset)
admin.site.register(Secret)
admin.site.register(ScrapingCode)
admin.site.register(Monitor)
