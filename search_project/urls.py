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
    path("", views.search_view, name="search_view"),
    path("search/", views.search_view, name="search_view"),
    path("product/new/", views.product_create, name="product_create"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("product/<int:pk>/edit/", views.product_update, name="product_update"),
    path("product/<int:pk>/delete", views.product_delete, name="product_delete"),
    path("product/", views.product_list, name="product_list"),
    # お気に入り機能
    path("favorites/add/<int:product_id>/", favorite_add, name="favorite_add"),
    path("favorites/remove/<int:product_id>/", favorite_remove, name="favorite_remove"),
    # 検索履歴機能
    path("search_history/", search_history_view, name="search_history"),
    # ユーザー認証機能
    path("register/", register, name="register"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    # プロフィールおよびパスワード変更
    path("profile/", profile, name="profile"),
    path("change_password/", change_password, name="change_password"),
    path("search_history/", search_history_view, name="search_history"),
    path("search_history/", views.search_history_view, name="search_history"),
    path(
        "search_history/delete/<int:history_id>/",
        views.delete_search_history,
        name="delete_search_history",
    ),
    path(
        "recommendation/",
        personalized_recommendation,
        name="personalized_recommendation",
    ),  # 追加
    path("favorites/", views.favorite_list, name="favorite_list"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
