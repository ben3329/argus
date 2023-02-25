from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# router = DefaultRouter()
# router.register(r'asset', AssetViewSet)
# router.register(r'secret', SecretsViewSet)
# router.register(r'scrap', ScrapingCodesViewSet)
# router.register(r'monitoring', MonitoringViewSet)

app_name = 'monitoring'

urlpatterns = [
    # path('', include(router.urls)),
    path('', index, name='index'),
    path('<int:asset_id>/', detail, name='detail'),
    path('mon/create/<int:asset_id>/', monitoring_create, name='mon_create'),
    path('asset/create/', asset_create, name='asset_create')
]