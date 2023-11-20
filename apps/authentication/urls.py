from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from .views import SigninView, LogoutView, CustomPasswordChangeView
from django.contrib.auth.views import (PasswordResetDoneView, PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from apps.authentication.views import CustomPasswordResetView

from apps.gym_hub.views import DataUploadTaskListView

urlpatterns = [
    path('login/', SigninView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('', HomeView.as_view(), name='home'),
    path('password-change/', CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('', DataUploadTaskListView.as_view(), name='home'),
    path('password-reset/', CustomPasswordResetView.as_view(template_name='registration/password_reset.html', html_email_template_name='registration/password_reset_email.html'),name='password-reset'),

    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),

    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),

]
