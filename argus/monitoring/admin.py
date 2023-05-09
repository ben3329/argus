from django.contrib import admin

# Register your models here.
from .models import *

# Register your models here.
admin.site.register(Asset)
admin.site.register(AccessCredential)
admin.site.register(BuiltInScript)
admin.site.register(UserDefinedScript)
admin.site.register(Monitor)
admin.site.register(Scrape)
admin.site.register(ScrapeData)

