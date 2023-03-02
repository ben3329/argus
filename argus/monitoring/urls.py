from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from monitoring import views

# router = DefaultRouter()
# router.register(r'asset', AssetViewSet)
# router.register(r'secret', SecretsViewSet)
# router.register(r'scrap', ScrapingCodesViewSet)
# router.register(r'monitoring', MonitoringViewSet)

app_name = 'monitoring'

urlpatterns = [
    # path('', include(router.urls)),
    path('', RedirectView.as_view(url='dashboard/')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('asset/', views.asset, name='asset'),
    path('monitor/', views.monitor, name='monitor'),
    path('secret/', views.secret, name='secret'),
    path('scraping_code/', views.scraping_code, name='scraping_code'),
    path('config/', views.config, name='config'),
]