from rest_framework import viewsets, permissions,status
from .models import Payment, Pitch, Booking
from .serializers import PaymentSerializer, PitchSerializer, BookingSerializer
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
import stripe


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
        if amount <= 0:
             raise ValidationError("Invalid booking amount.")

        # جلب السعر الحقيقي من قاعدة البيانات
        amount = booking.total_price

        # إنشاء سجل الدفع
        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            status="Pending"
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

            payment.status = "Failed"
            payment.save()

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        

stripe.api_key = settings.STRIPE_SECRET_KEY
class PaymentWebhookView(View):

    def post(self, request, *args, **kwargs):

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=sig_header,
                secret=settings.STRIPE_WEBHOOK_SECRET,
            )

        except ValueError:
            return HttpResponse(status=400)

        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        payment_intent = event["data"]["object"]
        payment_id = payment_intent["metadata"]["payment_id"]

        try:
            payment = Payment.objects.get(id=payment_id)

        except Payment.DoesNotExist:
            return HttpResponse(status=404)

        if event["type"] == "payment_intent.succeeded":

            payment.status = "Completed"
            payment.transaction_id = payment_intent["id"]
            payment.save()

            booking = payment.booking
            booking.status = "Confirmed"
            booking.save()

        elif event["type"] == "payment_intent.payment_failed":

            payment.status = "Failed"
            payment.save()

            booking = payment.booking
            booking.status = "Canceled"
            booking.save()

        return HttpResponse(status=200)