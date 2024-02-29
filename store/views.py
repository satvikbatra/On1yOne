from django.shortcuts import render

# Create your views here.
def signup(request):
    context = {}
    return render(request, 'store/signup.html', context)

def login(request):
    context = {}
    return render(request, 'store/login.html', context)

def home(request):
    context = {}
    return render(request, 'store/home.html', context)

def store(request):
    context = {}
    return render(request, 'store/store.html', context)

def cart(request):
    context = {}
    return render(request, 'store/cart.html', context)

def checkout(request):
    context = {}
    return render(request, 'store/checkout.html', context)