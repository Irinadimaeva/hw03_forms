# Из приложения django.contrib.auth нужный view-класс
import django.contrib.auth.views as authViews
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    # Полный адрес страницы регистрации - auth/signup/,
    # но префикс auth/ обрабатывется в головном urls.py
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        # В описании обработчика укажем шаблон,
        # который должен применяться для отображения возвращаемой страницы.
        # Во view-классах так можно!
        authViews.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        authViews.LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    path(
        'password_change/',
        authViews.PasswordChangeView.as_view(),
        name='password_change'
    ),
    path(
        'password_change/done/',
        authViews.PasswordChangeDoneView.as_view(),
        name='password_change_done'
    ),

    path(
        'password_reset/',
        authViews.PasswordResetView.as_view(),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        authViews.PasswordResetDoneView.as_view(),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        authViews.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        authViews.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'
    ),
]
