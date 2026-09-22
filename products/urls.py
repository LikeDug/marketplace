from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.catalog, name="catalog"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(template_name="registration/login.html", next_page="catalog"), name="login"),
    path("logout/", LogoutView.as_view(next_page="catalog"), name="logout"),
    path("cart/", views.cart_detail, name="cart"),
    path("cart/add/<int:pk>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:pk>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:pk>/", views.cart_update, name="cart_update"),
]
