from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('/login')
        else:
            messages.error(request, 'Cannot create account, Try Again!!!')
    else:
        form = UserCreationForm()
    context = {'form': form}
    return render(request, 'store/signup.html', context)


def login_view(request):
    if request.method =='POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Incorrect or Username!!!')
    else:
        form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'store/login.html', context)

def home(request):
    context = {}
    return render(request, 'store/home.html', context)

def store_t_shirt(request):
    context = {}
    return render(request, 'store/store_tshirt.html', context)

def store_hoodie(request):
    context = {}
    return render(request, 'store/store_hoodie.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        order = {'get_cart_total':0, 'get_cart_items':0}
        items = []
    context = {'items':items, 'order':order}
    return render(request, 'store/cart.html', context)


def checkout(request):
    # if request.user.is_authenticated:
    #     customer = request.user.customer
    #     order, created = Order.objects.get_or_create(customer=customer, complete=False)
    #     items = order.orderitem_set.all()
    # else:
    #     order = {'get_cart_total':0, 'get_cart_items':0}
    #     items = []
    # context = {'items':items, 'order':order}
    context = {}
    return render(request, 'store/checkout.html', context)

