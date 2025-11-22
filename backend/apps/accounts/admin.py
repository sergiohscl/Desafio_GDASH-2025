from django.contrib import admin
from apps.accounts.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active', 'avatar')
    search_fields = ('username', 'email')
    list_filter = ('is_active',)
