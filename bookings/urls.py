from django.urls import path ,include
from rest_framework.routers import DefaultRouter
from .views import PaymentCreateView, PitchViewSet, BookingViewSet,PaymentWebhookView
router=DefaultRouter()
router.register('pitch/',PitchViewSet,basename='pitch')
router.register('book/',BookingViewSet,basename='booking')
router.register('payment/',PaymentCreateView,basename='payment')
router.register('webhook/',PaymentWebhookView,basename='webhook')


urlpatterns=[
    path('',include(router.urls))
    
]