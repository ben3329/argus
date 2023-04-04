from django.contrib import admin

# Register your models here.
from .models import Asset, AccessCredential, Script, Monitor

# Register your models here.
admin.site.register(Asset)
admin.site.register(AccessCredential)
admin.site.register(Script)
admin.site.register(Monitor)
