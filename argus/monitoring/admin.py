from django.contrib import admin

# Register your models here.
from .models import Assets, Secrets, SSHAccessInfo, Monitoring

# Register your models here.
admin.site.register(Assets)
admin.site.register(Secrets)
admin.site.register(SSHAccessInfo)
admin.site.register(Monitoring)
