from django.db import models
from django.contrib.auth.models import User
import os
from uuid import uuid4


def upload_to(instance, filename):
    ext = filename.split(".")[-1]  # ファイルの拡張子を保持
    filename = f"{uuid4().hex}.{ext}"  # ランダムなファイル名を生成
    return os.path.join("images", filename)


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image = models.ImageField(
        upload_to=upload_to, blank=True, null=True
    )  # 画像フィールドを修正

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """お気に入り商品を保存するモデル"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class SearchHistory(models.Model):
    """検索履歴モデル"""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query} ({self.searched_at})"
