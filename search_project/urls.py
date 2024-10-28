from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import (
    favorite_add,
    favorite_remove,
    search_history_view,
    register,
    profile,
    change_password,
    personalized_recommendation,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),  # トップページへのルート
    path("search/", views.search_view, name="search_view"),
    path("product/new/", views.product_create, name="product_create"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path(
        "product/<int:product_id>/submit_review/",
        views.submit_review,
        name="submit_review",
    ),
    path("product/<int:pk>/edit/", views.product_update, name="product_update"),
    path("product/<int:pk>/delete", views.product_delete, name="product_delete"),
    path("product/", views.product_list, name="product_list"),
    path("favorites/add/<int:product_id>/", views.favorite_add, name="favorite_add"),
    path(
        "favorites/remove/<int:product_id>/",
        views.favorite_remove,
        name="favorite_remove",
    ),
    path("search_history/", views.search_history_view, name="search_history"),
    path("register/", views.register, name="register"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("change_password/", views.change_password, name="change_password"),
    path(
        "recommendation/",
        views.personalized_recommendation,
        name="personalized_recommendation",
    ),
    path("favorites/", views.favorite_list, name="favorite_list"),
    path("cart/", views.cart_view, name="cart_view"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "cart/remove/<int:cart_item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path("checkout/", views.checkout, name="checkout"),
    path("about/", views.about, name="about"),
    path("submit/", views.submit, name="submit"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("contact/", views.contact, name="contact"),
    path(
        "delete_search_history/<int:history_id>/",
        views.delete_search_history,
        name="delete_search_history",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
