# Из приложения django.contrib.auth нужный view-класс
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
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
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    path(
        'password_reset/',
        PasswordResetView.as_view(),
        name='password_reset_form'
    ),
]
