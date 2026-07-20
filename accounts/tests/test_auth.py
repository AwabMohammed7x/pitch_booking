from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class AuthTests(TestCase):

    def setUp(self):
        # تجهيز API Client قبل كل Test
        self.client = APIClient()

    def test_register_user(self):
        # البيانات التي سنرسلها للـ API
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "StrongPassword123",
            "first_name": "Test",
            "last_name": "User"
        }

        # إرسال Request
        response = self.client.post(
            "/auth/users/",
            data,
            format="json"
        )

        # التأكد أن التسجيل نجح
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        # التأكد أن المستخدم تم إنشاؤه في قاعدة البيانات
        self.assertTrue(
            User.objects.filter(username="awab").exists()
        )


