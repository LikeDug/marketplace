from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product
from .views import add_images


class ProductImageTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Техника", slug="texnika")

    def test_product_has_image_url_field(self):
        field = Product._meta.get_field("image_url")
        self.assertEqual(field.__class__.__name__, "URLField")

    def test_add_images_uses_product_image_url_when_present(self):
        product = Product.objects.create(
            category=self.category,
            name="Смартфон",
            description="Новый смартфон",
            price="299.99",
            image_url="https://example.com/phone.jpg",
        )

        result = add_images([product])

        self.assertEqual(result[0].image_url, "https://example.com/phone.jpg")


class AccountAuthTest(TestCase):
    def test_register_creates_user(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "Strongpass123",
                "password2": "Strongpass123",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username="newuser").exists())
