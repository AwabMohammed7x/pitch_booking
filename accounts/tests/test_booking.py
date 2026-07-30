from datetime import timedelta

from django.http import response
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from bookings.models import Pitch, Booking


User = get_user_model()


class BookingTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def authenticate(self):
        # إنشاء مستخدم
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        # إنشاء Access Token
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)

        # إضافته في الـ Header
        self.client.credentials(
            HTTP_AUTHORIZATION=f"JWT {access_token}"
        )

    def test_booking_with_wrong_time(self):

        # Arrange
        self.authenticate()

        self.pitch = Pitch.objects.create(
            name="Test Pitch",
            price_per_hour=50
        )

        start_time = timezone.now() + timedelta(days=1, hours=2)
        end_time = timezone.now() + timedelta(days=1)

        data = {
            "pitch": self.pitch.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        # Act
        response = self.client.post(
            "/api/book/",
            data,
            format="json"
        )

        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "غير منطقي: وقت النهاية يجب أن يكون بعد وقت البداية.",
            str(response.data)
        )

        self.assertEqual(
            Booking.objects.count(),
            0
        )

    def test_booking_in_past_time(self):

        # Arrange
        self.authenticate()

        self.pitch = Pitch.objects.create(
            name="Test Pitch",
            price_per_hour=50
        )

        start_time = timezone.now() - timedelta(days=1, hours=2)
        end_time = timezone.now() - timedelta(days=1)

        data = {
            "pitch": self.pitch.id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        # Act
        response = self.client.post(
            "/api/book/",
            data,
            format="json"
        )
        
        # Assert
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "عفواً، لا يمكنك الحجز في وقت مضى.",  
            str(response.data)
        )

        self.assertEqual(
            Booking.objects.count(),
            0
        )
        print(response.status_code)
        print(response.headers)

    def test_booking_in_same_time(self):
  
    # ---------------- Arrange ----------------

        self.authenticate()

        self.pitch = Pitch.objects.create(
            name="Test Pitch",
            price_per_hour=50
        )

        base_time = timezone.now() + timedelta(days=1)

        # إنشاء حجز موجود مسبقاً
        Booking.objects.create(
            user=self.user,
            pitch=self.pitch,
            start_time=base_time,
            end_time=base_time + timedelta(hours=2),
            total_price=100,
            status="Pending"
        )

        self.assertEqual(
            Booking.objects.count(),
            1
        )

        # محاولة إنشاء حجز متداخل
        data = {
            "pitch": self.pitch.id,
            "start_time": (base_time + timedelta(hours=1)).isoformat(),
            "end_time": (base_time + timedelta(hours=3)).isoformat(),
        }

        # ---------------- Act ----------------

        response = self.client.post(
            "/api/book/",
            data,
            format="json"
        )

        # ---------------- Assert ----------------

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertIn(
            "عفواً، هذا الملعب محجوز في هذا الوقت. يرجى اختيار وقت آخر.",
            str(response.data)
        )

        self.assertEqual(
            Booking.objects.count(),
            1
        )