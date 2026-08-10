from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


admin.site.site_header = "Think Technology"
admin.site.site_title = "Think Technology - Administração"
admin.site.index_title = "Painel Administrativo"


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "username",
        "email",
        "status_usuario",
        "is_staff",
        "date_joined",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = ("username",)

    @admin.display(description="Status")
    def status_usuario(self, obj):
        return "Ativo" if obj.is_active else "Inativo"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            "Informações pessoais",
            {
                "fields": (
                    "email",
                )
            },
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Datas",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )