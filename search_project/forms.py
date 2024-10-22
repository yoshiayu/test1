from django import forms
from .models import Product


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
        fields = ["name", "description", "price", "category", "image"]  # 'image' を追加
        labels = {
            "name": "商品名",
            "description": "説明",
            "price": "価格",
            "category": "カテゴリ",
            "image": "商品画像",  # 画像のラベルを追加
        }
