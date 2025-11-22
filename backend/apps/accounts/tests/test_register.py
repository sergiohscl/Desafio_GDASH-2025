from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class RegisterAPIViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('register')
        self.valid_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Django13$",
            "password2": "Django13$"
        }
        self.invalid_data_password_mismatch = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Django13$",
            "password2": "Django13"
        }
        self.existing_user_data = {
            "username": "existinguser",
            "email": "existinguser@example.com",
            "password": "Django13$",
            "password2": "Django13$"
        }

        User.objects.create_user(
            username="existinguser",
            email="existinguser@example.com",
            password="Django13$"
        )

        self.avatar = SimpleUploadedFile(
            "avatar.jpg", b"image_content", content_type="image/jpeg"
        )

    def test_register_success(self):
        self.valid_data['avatar'] = self.avatar

        response = self.client.post(
            self.url, self.valid_data, format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("token", response.data)

    def test_register_password_mismatch(self):
        response = self.client.post(
            self.url,
            self.invalid_data_password_mismatch,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertIn("password", response.data["errors"])

    def test_register_existing_email(self):
        self.existing_user_data['avatar'] = self.avatar

        response = self.client.post(
            self.url,
            self.existing_user_data,
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertIn("email", response.data["errors"])
