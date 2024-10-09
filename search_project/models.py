from django.db import models


class Category(models.Model):
    """カテゴリーテーブル

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品テーブル

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, default=1
    )  # 1はカテゴリID

    def __str__(self):
        return self.name
