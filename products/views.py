from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Category, Product


PRODUCT_KEYWORDS = {
    1: "sports-ball", 2: "running-shoes", 3: "smartphone", 4: "laptop",
    5: "wireless-headphones", 6: "smart-lamp", 7: "fitness-tracker", 8: "skincare-set",
    9: "backpack", 10: "dumbbells", 11: "resistance-bands", 12: "jump-rope",
    13: "sports-bag", 14: "foam-roller", 15: "workout-gloves",
    16: "smartphone", 17: "smartphone", 18: "smartphone", 19: "smartphone",
    20: "smartphone", 21: "smartphone", 22: "smartphone", 23: "smartphone",
    24: "business-laptop", 25: "gaming-laptop", 26: "student-laptop", 27: "laptop",
    28: "office-laptop", 29: "laptop", 30: "laptop", 31: "laptop",
    32: "phone-charger", 33: "phone-case", 34: "power-bank", 35: "usb-c-cable",
    36: "phone-stand", 37: "smartwatch", 38: "bluetooth-speaker",
    39: "aroma-diffuser", 40: "blanket", 41: "towels", 42: "storage-organizer",
    43: "desk-lamp", 44: "humidifier", 45: "vase", 46: "pillow",
    47: "face-cream", 48: "face-serum", 49: "micellar-water", 50: "hair-mask",
    51: "lip-balm", 52: "makeup-brushes", 53: "face-cleanser", 54: "perfume-bottle",
}


def add_images(products):
    for product in products:
        if product.image_url:
            continue
        keyword = PRODUCT_KEYWORDS.get(product.pk, "product")
        product.image_url = f"https://loremflickr.com/640/480/{keyword}?lock={product.pk}"
    return products


def cart_count(request):
    return sum(request.session.get("cart", {}).values())


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("catalog")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def catalog(request):
    products = Product.objects.filter(available=True).select_related("category")
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if selected_category:
        products = products.filter(category__slug=selected_category)
    products = add_images(products)

    return render(request, "products/storefront_images.html", {
        "products": products, "categories": categories, "query": query,
        "selected_category": selected_category, "cart_count": cart_count(request),
    })


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk, available=True)
    add_images([product])
    return render(request, "products/product_images.html", {"product": product, "cart_count": cart_count(request)})


@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, available=True)
    cart = request.session.get("cart", {})
    key = str(product.pk)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


@require_POST
def cart_remove(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    request.session.modified = True
    return redirect("cart")


@require_POST
def cart_update(request, pk):
    cart = request.session.get("cart", {})
    key = str(pk)
    if key in cart:
        if request.POST.get("action") == "increase":
            cart[key] += 1
        elif cart[key] > 1:
            cart[key] -= 1
        else:
            cart.pop(key)
        request.session["cart"] = cart
        request.session.modified = True
    return redirect("cart")


def cart_detail(request):
    cart = request.session.get("cart", {})
    products = Product.objects.filter(pk__in=cart).select_related("category")
    add_images(products)
    items = []
    total = 0
    for product in products:
        quantity = cart[str(product.pk)]
        line_total = product.price * quantity
        items.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
    return render(request, "products/cart_images.html", {"items": items, "total": total, "cart_count": cart_count(request)})
