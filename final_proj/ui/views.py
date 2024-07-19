from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignUpForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Product, Review
from .forms import ProductForm, ReviewForm


def landing_page(request):
    return render(request, 'index.html')


def home(request):
    return render(request, 'home.html')


def logout_view(request):
    logout(request)
    return redirect('landing_page')


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Load the profile instance created by the signal
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('landing_page')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'profile.html', {'user': request.user})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all()
    return render(request, 'product_detail.html', {'product': product, 'reviews': reviews})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'delete_product.html', {'product': product})


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form})


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        return redirect('product_detail', pk=review.product.pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=review.product.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form})


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if request.user != review.user:
        return redirect('product_detail', pk=review.product.pk)
    product_pk = review.product.pk
    if request.method == 'POST':
        review.delete()
        return redirect('product_detail', pk=product_pk)
    return render(request, 'delete_review.html', {'review': review})
