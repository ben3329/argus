from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
app_name = 'common'

urlpatterns = [
    path('login/', views.CommonLoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('signup/', views.signup, name='signup'),
]