from django.urls import path

from . import views

app_name = 'getter'
urlpatterns = [
    path('', views.main, name='main'),
    path('export_price_regions/', views.export_price_regions,
         name='export_price_regions'),
    path('export_sell_price_rules/', views.export_sell_price_rules,
         name='export_sell_price_rules'),
    path('export_seazone_listings/', views.export_seazone_listings,
         name='export_seazone_listings')
]
