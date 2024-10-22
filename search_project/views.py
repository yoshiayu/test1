from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Favorite, SearchHistory
from .forms import ProductForm, SearchForm
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.shortcuts import render, redirect


def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)  # request.FILES を追加
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()
    return render(request, "product_form.html", {"form": form})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES, instance=product
        )  # request.FILES を追加
        if form.is_valid():
            form.save()
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, "product_form.html", {"form": form, "product": product})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    return render(request, "product_detail.html", {"product": product})


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    # product オブジェクトをテンプレートに渡す
    return render(request, "product_form.html", {"form": form, "product": product})


def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect("product_list")
    return render(request, "product_confirm_delete.html", {"product": product})


def product_list(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})


def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all()  # クエリセットの初期化

    if form.is_valid():
        query = form.cleaned_data["query"]
        if query:
            results = results.filter(
                name__icontains=query
            )  # ここでの filter はクエリセットに適用
            # 検索履歴を保存
            if request.user.is_authenticated:  # ログインしているユーザーの場合のみ保存
                SearchHistory.objects.create(user=request.user, query=query)

    # カテゴリフィルタリング
    category_name = request.GET.get("category")
    if category_name:
        try:
            # カテゴリ名に基づいてカテゴリIDを取得
            category = Category.objects.get(name=category_name)
            results = results.filter(category_id=category.id)
        except Category.DoesNotExist:
            results = results.none()  # 存在しないカテゴリの場合、結果を空にする
            category = None

    # 価格のフィルタリング（最低価格・最高価格）
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        results = results.filter(price__gte=min_price)
    if max_price:
        results = results.filter(price__lte=max_price)

    # 並び替え処理
    sort_by = request.GET.get("sort", "name")
    if sort_by == "price_asc":
        results = results.order_by("price")
    elif sort_by == "price_desc":
        results = results.order_by("-price")

    # クエリセットをリストに変換せず、直接Paginatorに渡す
    paginator = Paginator(results, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request, "search.html", {"form": form, "page_obj": page_obj, "results": results}
    )


@login_required
def favorite_list(request):
    # ログインしているユーザーのお気に入り商品を取得
    favorites = Favorite.objects.filter(user=request.user).select_related("product")
    return render(request, "favorite_list.html", {"favorites": favorites})


@login_required
def favorite_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, product=product
    )
    if created:
        return redirect("product_detail", pk=product_id)
    else:
        # 既にお気に入りにある場合の処理
        return redirect("product_detail", pk=product_id)


@login_required
def favorite_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite = Favorite.objects.filter(user=request.user, product=product).first()
    if favorite:
        favorite.delete()
    return redirect("product_detail", pk=product_id)


@login_required
def search_history_view(request):
    # ログインしているユーザーの検索履歴を取得
    histories = SearchHistory.objects.filter(user=request.user).order_by("-searched_at")
    return render(request, "search_history.html", {"histories": histories})


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


def create_product(request):
    if request.method == "POST":
        form = ProductForm(
            request.POST, request.FILES
        )  # 画像ファイルは request.FILES で受け取る
        if form.is_valid():
            form.save()
            return redirect("product_list")  # 商品一覧などにリダイレクト
    else:
        form = ProductForm()

    return render(request, "create_product.html", {"form": form})
