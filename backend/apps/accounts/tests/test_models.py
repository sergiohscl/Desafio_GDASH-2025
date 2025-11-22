from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import Usuario


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword',
        )

    def test_usuario_criacao(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.is_active)

    def test_usuario_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_usuario_avatar(self):
        avatar_mock = SimpleUploadedFile(
            "avatar.jpg", b"file_content", content_type="image/jpeg"
        )
        self.user.avatar = avatar_mock
        self.user.save()
        self.assertTrue(self.user.avatar.name.startswith('avatars/'))

    def test_usuario_email_unico(self):
        with self.assertRaises(Exception):
            Usuario.objects.create_user(
                username='testuser2',
                email='testuser@example.com',
                password='securepassword2',
            )
