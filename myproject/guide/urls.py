from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    path('search/', views.search_product, name='search_product'),
    path('contact/', views.contact, name='contact'),
    path('add-product-type/', views.add_product_type, name='add_product_type'),
    path('add-product-model/', views.add_product_model, name='add_product_model'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
]