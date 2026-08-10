from django.contrib import admin
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from django.urls import path

from app.products.repository import ProductRepository
from users.admin import CustomUserAdmin
from users.models import User


class ChallengeAdminSite(AdminSite):
    site_header = "Think Technology"
    site_title = "Think Technology - Administração"
    index_title = "Painel Administrativo"
    index_template = "admin/custom_index.html"
    enable_nav_sidebar = False

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "products/",
                self.admin_view(self.products_view),
                name="products_view",
            ),
        ]

        return custom_urls + urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["products_url"] = "products/"

        return super().index(
            request,
            extra_context=extra_context,
        )

    def products_view(self, request):
        repo = ProductRepository()

        try:
            products = repo.list()
        finally:
            repo.close()

        context = {
            **self.each_context(request),
            "title": "Produtos cadastrados",
            "products": products,
        }

        return TemplateResponse(
            request,
            "admin/products/list.html",
            context,
        )


admin_site = ChallengeAdminSite(name="challenge_admin")

admin_site.register(User)