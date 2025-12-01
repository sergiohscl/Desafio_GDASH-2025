from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LoginAPIViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login')
        self.email = "testuser@example.com"
        self.password = "Django13$"
        self.user = User.objects.create_user(
            username="testuser",
            email=self.email,
            password=self.password
        )
        Token.objects.filter(user=self.user).delete()
        self.token = Token.objects.create(user=self.user)

    def test_login_success(self):
        data = {
            "email": self.email,
            "password": self.password
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["message"], "Login bem-sucedido!")

    def test_login_invalid_credentials(self):
        data = {
            "email": "wrongemail@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["errors"], "Credenciais inválidas.")

    def test_login_missing_credentials(self):
        data = {
            "email": self.email,
            "password": ""
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)
        self.assertEqual(
            response.data["errors"],
            "E-mail e senha são obrigatórios."
        )
