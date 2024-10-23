from django import forms
from .models import Product, Review


class SearchForm(forms.Form):
    query = forms.CharField(
        label="検索キーワード",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "検索したいキーワードを入力"}),
    )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "category", "image"]
        labels = {
            "name": "商品名",
            "description": "説明",
            "price": "価格",
            "category": "カテゴリ",
            "image": "商品画像",
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        labels = {
            "rating": "評価",
            "comment": "コメント",
        }
        widgets = {
            "rating": forms.Select(choices=[(i, i) for i in range(1, 6)]),  # 1-5の評価
            "comment": forms.Textarea(attrs={"rows": 4}),
        }
