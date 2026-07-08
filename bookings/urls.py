from django.urls import path ,include
from rest_framework.routers import DefaultRouter
from .views import PaymentCreateView, PitchViewSet, BookingViewSet,PaymentWebhookView
router=DefaultRouter()
router.register('pitch/',PitchViewSet,basename='pitch')
router.register('book/',BookingViewSet,basename='booking')

urlpatterns = [
    path("", include(router.urls)),

    path(
        "payments/create/",
        PaymentCreateView.as_view(),
        name="payment-create",
    ),

    path(
        "payments/webhook/",
        PaymentWebhookView.as_view(),
        name="payment-webhook",
    ),
]