from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError
from ..models import Usuario


class RegisterManager:
    @staticmethod
    def validate(data):
        # Valida se as senhas coincidem
        if data['password'] != data['password2']:
            raise ValidationError({"password": "As senhas não correspondem."})

        # Valida se o email já está em uso
        if Usuario.objects.filter(email=data['email']).exists():
            raise ValidationError({"email": "Este email já está registrado."})

        # Validação de senha
        try:
            validate_password(data['password'])
        except ValidationError as e:
            raise ValidationError({"password": e.messages})

        return data

    @staticmethod
    def create(data):
        avatar = data.pop('avatar', None)
        data.pop('password2', None)

        user = Usuario.objects.create_user(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])
        if avatar:
            if isinstance(avatar, list):
                avatar = avatar[0]
            user.avatar = avatar
            # if not isinstance(avatar, str):
            #     user.avatar = avatar

        user.save()
        return user
