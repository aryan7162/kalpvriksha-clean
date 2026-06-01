from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'cities', views.CityViewSet, basename='city')
router.register(r'sublocations', views.SublocationViewSet, basename='sublocation')

urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.home, name='home'),
    path('properties/', views.property_list, name='property_list'),
    path('happy-families/', views.happy_families, name='happy_families'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('faq/', views.faq, name='faq'),
    path('properties/<slug:city_slug>/', views.property_list, name='properties_by_city'),
    path('<slug:slug>/', views.property_detail, name='property_detail'),
]