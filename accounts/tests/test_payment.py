from datetime import timedelta
from unittest.mock import Mock, patch
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from bookings.models import Payment, Pitch,Booking
User = get_user_model()

class PaymentTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def authenticate(self): 
        # إنشاء مستخدم
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword"
        )

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT {access_token}"
        )

    @patch('bookings.views.stripe.PaymentIntent.create')
    def test_success_payment(self, mock_create):
        mock_create.return_value = Mock(
        id="pi_123456789",
        client_secret="secret_test"
        )

        self.authenticate()

        # إنشاء ملعب
        self.pitch = Pitch.objects.create(
            name="Test Pitch",
            price_per_hour=50
        )

        # إنشاء حجز
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)

        booking = Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            start_time=start_time,
            end_time=end_time,
            total_price=100,  # 2 hours * 50 per hour
            status='Confirmed'
        )

    # بيانات الدفع
        payment_data = {
            "booking": booking.id,
        }
        
      # إرسال طلب الدفع
        response = self.client.post(
            "/api/payments/create/",
            payment_data,
            format="json"
        )

        # التأكد من نجاح الدفع
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        mock_create.assert_called_once()
        self.assertEqual(Payment.objects.count(), 1)