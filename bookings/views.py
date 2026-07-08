from rest_framework import viewsets, permissions
from .models import Payment, Pitch, Booking
from .serializers import PaymentSerializer, PitchSerializer, BookingSerializer

# 1. فيو الملاعب: عرض فقط (Read-Only)
class PitchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Pitch.objects.all()
    serializer_class = PitchSerializer
    permission_classes = [permissions.AllowAny] # الكل مسموح له يشوف الملاعب


class BookingViewSet(viewsets.ModelViewSet):
    
    serializer_class =BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
         serializer.save(user=self.request.user)

from rest_framework import status, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Payment
from .serializers import PaymentSerializer


import stripe

from django.conf import settings

from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Payment
from .serializers import PaymentSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentCreateView(CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = serializer.validated_data["booking"]

        # التأكد أن الحجز يخص المستخدم
        if booking.user != request.user:
            raise PermissionDenied(
                "You cannot pay for another user's booking."
            )

        # التأكد من عدم وجود عملية دفع سابقة
        if Payment.objects.filter(booking=booking).exists():
            raise ValidationError(
                "This booking has already been paid."
            )

        # جلب السعر الحقيقي من قاعدة البيانات
        amount = booking.total_price

        # إنشاء سجل الدفع
        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            status="pending"
        )

        try:

            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),
                currency="usd",
                metadata={
                    "payment_id": payment.id,
                    "booking_id": booking.id,
                    "user_id": request.user.id,
                },
            )

            payment.transaction_id = intent.id
            payment.save()

            return Response(
                {
                    "message": "Payment Intent created successfully.",
                    "client_secret": intent.client_secret,
                    "payment_id": payment.id,
                    "amount": amount,
                },
                status=status.HTTP_201_CREATED,
            )

        except stripe.error.StripeError as e:

            payment.status = "failed"
            payment.save()

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )