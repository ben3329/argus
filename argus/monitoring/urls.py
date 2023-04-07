from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import RedirectView
from monitoring import views

app_name = 'monitoring'

router = DefaultRouter()
router.register(r'assets', views.AssetViewSet)
router.register(r'access_credentials', views.AccessCredentialViewSet)
router.register(r'scripts', views.ScriptViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('', RedirectView.as_view(url='dashboard/')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('asset/', views.asset, name='asset'),
    path('monitor/', views.monitor, name='monitor'),
    path('access_credential/', views.access_credential, name='access_credential'),
    path('script/', views.script, name='script'),
    path('config/', views.config, name='config'),
    path('api/', include(router.urls)),
]
