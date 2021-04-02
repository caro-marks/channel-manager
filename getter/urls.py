from django.urls import path

from . import views

app_name = 'getter'
urlpatterns = [
    path('', views.main, name='main')
]
