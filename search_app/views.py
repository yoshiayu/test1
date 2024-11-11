# 必要なモジュールとクラスをインポート
from datetime import timezone
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from .models import CartItem, Cart, Product, Category, Favorite, SearchHistory, Review
from .forms import ProductForm, SearchForm, ReviewForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.contrib import messages
from search_app import models
import stripe
from django.conf import settings


# ホームページの表示
def index(request):
    # テストメッセージを含むテンプレートをレンダリング
    return render(
        request, "index.html", {"test_message": "テンプレートが読み込まれています"}
    )


# 商品の作成ページの処理
def product_create(request):
    if request.method == "POST":  # POSTリクエストの確認
        form = ProductForm(request.POST, request.FILES)  # フォームデータの取得
        if form.is_valid():  # フォームの有効性を確認
            form.save()  # 商品データを保存
            return redirect("product_list")  # 商品一覧にリダイレクト
    else:
        form = ProductForm()  # 空のフォームで初期化
    return render(request, "product_form.html", {"form": form})


# 商品の更新ページの処理
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)  # 指定された商品を取得
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES, instance=product
        )  # フォームデータの取得
        if form.is_valid():
            form.save()  # 商品情報を更新
            return redirect("product_detail", pk=product.pk)  # 商品詳細にリダイレクト
    else:
        form = ProductForm(instance=product)  # 現在の情報でフォームを初期化
    return render(request, "product_form.html", {"form": form, "product": product})


# 商品の詳細ページの表示
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)  # 指定された商品を取得
    reviews = product.reviews.all()  # 商品に紐づく全てのレビューを取得
    review_form = ReviewForm()  # レビュー投稿用のフォームを初期化

    if request.method == "POST":
        if request.user.is_authenticated:  # ユーザーがログイン中か確認
            review_form = ReviewForm(request.POST)  # レビューのフォームデータを取得
            if review_form.is_valid():  # フォームの有効性を確認
                new_review = review_form.save(commit=False)
                new_review.product = product  # レビューに商品を紐づけ
                new_review.user = request.user  # レビューにユーザーを紐づけ
                new_review.save()  # レビューを保存
                return redirect(
                    "product_detail", pk=product.pk
                )  # 商品詳細にリダイレクト
        else:
            return redirect("login")  # ログインページにリダイレクト

    return render(
        request,
        "product_detail.html",
        {"product": product, "reviews": reviews, "review_form": review_form},
    )


# レビューの投稿処理
@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # 指定された商品を取得

    if request.method == "POST":
        rating = request.POST.get("rating")  # レビューの評価を取得
        comment = request.POST.get("comment", "")  # コメントを取得

        if rating:
            # 新しいレビューを作成
            Review.objects.create(
                product=product, user=request.user, rating=rating, comment=comment
            )
            messages.success(request, "レビューが投稿されました。")
        else:
            messages.error(request, "評価を選択してください。")

    return redirect("product_detail", pk=product_id)


# 個人向けのレコメンデーションの表示
@login_required
def personalized_recommendation(request):
    favorite_products = Favorite.objects.filter(user=request.user).values_list(
        "product", flat=True
    )  # ユーザーのお気に入り商品を取得

    search_keywords = SearchHistory.objects.filter(user=request.user).values_list(
        "query", flat=True
    )  # ユーザーの検索履歴を取得

    search_conditions = Q()  # 検索条件の初期化
    for keyword in search_keywords:
        search_conditions |= Q(
            name__icontains=keyword
        )  # キーワードに一致する条件を追加

    recommended_products = Product.objects.filter(
        Q(id__in=favorite_products) | search_conditions
    ).distinct()[
        :10
    ]  # レコメンド商品を取得

    return render(
        request,
        "personalized_recommendation.html",
        {"recommended_products": recommended_products},
    )


# 商品の削除処理
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)  # 指定された商品を取得
    if request.method == "POST":
        product.delete()  # 商品を削除
        return redirect("product_list")  # 商品一覧にリダイレクト
    return render(request, "product_confirm_delete.html", {"product": product})


# 商品一覧の表示
def product_list(request):
    products = Product.objects.all()  # 全商品の取得
    return render(request, "product_list.html", {"products": products})


# 検索機能
def search_view(request):
    form = SearchForm(request.GET or None)  # 検索フォームを初期化
    results = Product.objects.all()  # 初期のクエリセット

    if form.is_valid():
        query = form.cleaned_data["query"]  # フォームの入力データを取得
        if query:
            results = results.filter(
                name__icontains=query
            )  # 名前に一致する商品をフィルタリング
            if request.user.is_authenticated:
                SearchHistory.objects.create(
                    user=request.user, query=query
                )  # 検索履歴を保存

    category_name = request.GET.get("category")  # カテゴリのフィルタリング
    if category_name:
        try:
            category = Category.objects.get(name=category_name)
            results = results.filter(category_id=category.id)
        except Category.DoesNotExist:
            results = results.none()  # 該当するカテゴリがない場合結果を空に

    min_price = request.GET.get("min_price")  # 最小価格のフィルタリング
    max_price = request.GET.get("max_price")  # 最大価格のフィルタリング

    if min_price:
        results = results.filter(price__gte=min_price)
    if max_price:
        results = results.filter(price__lte=max_price)

    sort_by = request.GET.get("sort", "name")  # 並び順の指定
    if sort_by == "price_asc":
        results = results.order_by("price")
    elif sort_by == "price_desc":
        results = results.order_by("-price")

    paginator = Paginator(results, 8)  # ページネーション
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request, "search.html", {"form": form, "page_obj": page_obj, "results": results}
    )


# お気に入り商品リストの表示
@login_required
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related(
        "product"
    )  # ログイン中のユーザーのお気に入りを取得
    return render(request, "favorite_list.html", {"favorites": favorites})


# お気に入りに追加
@login_required
def favorite_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # 指定された商品を取得
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, product=product
    )
    return redirect("product_detail", pk=product_id)


# お気に入りから削除
@login_required
def favorite_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # 指定された商品を取得
    favorite = Favorite.objects.filter(user=request.user, product=product).first()
    if favorite:
        favorite.delete()  # お気に入りを削除
    return redirect("product_detail", pk=product_id)


# 検索履歴の表示
@login_required
def search_history_view(request):
    histories = SearchHistory.objects.filter(user=request.user).order_by(
        "-searched_at"
    )  # ユーザーの検索履歴を取得
    return render(request, "search_history.html", {"histories": histories})


# 検索履歴の削除
@login_required
def delete_search_history(request, history_id):
    history = get_object_or_404(SearchHistory, id=history_id, user=request.user)
    history.delete()  # 検索履歴を削除
    return redirect("search_history")


# ユーザー登録ビュー
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 登録後自動的にログイン
            return redirect("product_list")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})


# プロフィール表示
@login_required
def profile(request):
    return render(request, "profile.html")


# パスワード変更
@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(
                request, user
            )  # パスワード変更後にログアウトしないようにする
            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "change_password.html", {"form": form})


# 商品の新規作成
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "create_product.html", {"form": form})


# カートに商品を追加
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect("view_cart")


# カートの表示
@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(
        request, "cart.html", {"cart_items": cart_items, "total_price": total_price}
    )


# カートから商品を削除
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.delete()
    return redirect("view_cart")


# チェックアウト
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    if request.method == "POST":
        try:
            charge = stripe.Charge.create(
                amount=int(total_price * 100),
                currency="jpy",
                description="Order from ECサイト",
                source=request.POST["stripeToken"],
            )
            cart_items.delete()
            return redirect("checkout_success")
        except stripe.error.StripeError as e:
            return render(
                request,
                "checkout.html",
                {"error": str(e), "cart_items": cart_items, "total_price": total_price},
            )
    return render(
        request, "checkout.html", {"cart_items": cart_items, "total_price": total_price}
    )


# サイトの他の静的ページの表示
def about(request):
    return render(request, "about.html")


def submit(request):
    return render(request, "submit.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def contact(request):
    return render(request, "contact.html")


def terms_of_service(request):
    return render(request, "terms_of_service.html")


def faq(request):
    return render(request, "faq.html")


# 検索処理
def search(request):
    query = request.GET.get("q")
    if not query:
        raise Http404("Search query is required.")
    products = Product.objects.filter(name__icontains=query)
    history, _ = SearchHistory.objects.get_or_create(user=request.user, query=query)
    history.searched_at = timezone.now()
    history.save()
    return render(
        request, "search_results.html", {"query": query, "products": products}
    )


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user, product=product
    )

    if not created:
        # 既にカートに入っている場合、数量を1増やす
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart_view")


@login_required
def cart_view(request):
    # ログインしているユーザーのカートアイテムを取得
    cart_items = CartItem.objects.filter(user=request.user)
    # カート内の全商品の合計金額を計算
    total_price = sum(item.total_price() for item in cart_items)

    # カートページにデータをレンダリング
    return render(
        request, "cart.html", {"cart_items": cart_items, "total_price": total_price}
    )


# @login_required
# def add_to_cart(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

#     if not created:
#         cart_item.quantity += 1  # 既にカートにある場合は数量を増やす
#     cart_item.save()

#     return redirect("view_cart")  # カート画面にリダイレクト
