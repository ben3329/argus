from django.contrib import admin

# Register your models here.
from .models import Assets, Secrets, ScrapingCodes, Monitoring

# Register your models here.
admin.site.register(Assets)
admin.site.register(Secrets)
admin.site.register(ScrapingCodes)
admin.site.register(Monitoring)
