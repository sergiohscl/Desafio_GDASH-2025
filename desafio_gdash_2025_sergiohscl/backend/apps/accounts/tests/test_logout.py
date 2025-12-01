from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class LogoutAPIViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('logout')
        self.email = "testuser@example.com"
        self.password = "Django13$"
        self.user = User.objects.create_user(
            username="testuser",
            email=self.email,
            password=self.password
        )
        Token.objects.filter(user=self.user).delete()
        self.token = Token.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_logout_success(self):
        response = self.client.post(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"],
            "Logout realizado com sucesso!"
        )
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_logout_without_token(self):
        self.token.delete()
        response = self.client.post(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "Token inválido ou não encontrado."
        )
