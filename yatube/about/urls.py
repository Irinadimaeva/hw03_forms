from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path('author/', views.AboutAuthorStaticPage.as_view(), name='author'),
    path('tech/', views.AboutTechStaticPage.as_view(), name='tech'),
]
