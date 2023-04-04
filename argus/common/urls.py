from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    path('login/', views.CommonLoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_reset/', views.CommonPasswordResetView.as_view(),
         name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='common/password_reset_done.html'
    ), name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/',
         views.CommonPasswordResetConfirmView.as_view(
             template_name='common/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('signup/', views.signup, name='signup'),
]
