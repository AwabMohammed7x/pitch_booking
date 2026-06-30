from django.urls import path ,include
from rest_framework.routers import DefaultRouter
from .views import *
router=DefaultRouter()
router.register('pitch/',PitchViewSet,basename='pitch')
router.register('book/',BookingViewSet,basename='booking')


urlpatterns=[
    path('',include(router.urls))
    
]