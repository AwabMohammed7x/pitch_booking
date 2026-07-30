from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

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
            User.objects.filter(username="testuser").exists()
        )

    def test_login_user(self):

        self.user=User.objects.create_user(
            username="testuser2",
            email="testuser2@gmail.com",
            password="StrongPassword123"
        )

        # البيانات التي سنرسلها للـ API
        data = {
            "username": "testuser2",
            "password": "StrongPassword123"
        }

        # إرسال Request
        response = self.client.post(
            "/auth/jwt/create/",
            data,
            format="json"
        )

        # التأكد أن تسجيل الدخول نجح
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)

        self.assertIn("refresh", response.data)

    def test_login_with_wrong_password(self):

        user=User.objects.create_user(
            username="testuser3",
            email="testuser3@gmail.com",
            password="StrongPassword123"
        )

        # البيانات التي سنرسلها للـ API
        data = {
            "username": "testuser3",
            "password": "WrongPassword123"
        }

        # إرسال Request
        response = self.client.post(
            "/auth/jwt/create/",
            data,
            format="json"
        )

        # التأكد أن تسجيل الدخول فشل
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_login_with_valid_credentials(self):
        user=User.objects.create_user(
            username="testuser4",
            email="testuser4@gmail.com",
            password="StrongPassword123"
        )

        refersh=RefreshToken.for_user(user)

        access_token=str(refersh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')

        response=self.client.get('/auth/users/me/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_login_with_out_valid_credentials(self):
        
        response=self.client.get('/auth/users/me/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

