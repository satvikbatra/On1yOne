from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
# from .models import SIZES

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
    context = {}
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
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        order = {'get_cart_total':0, 'get_cart_items':0}
        items = []
    context = {'items':items, 'order':order}
    # context = {}
    return render(request, 'store/checkout.html', context)



from django.http import JsonResponse
from .models import Product, Order, OrderItem

def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_color = data.get('color')
        selected_size = data.get('size')


        # Log the received data for debugging
        print(f"Received color: {selected_color}, size: {selected_size}")

        # Check if the selected_size value is valid
        # if selected_size is None or selected_size not in Product.SIZES:
        #     print(f"Size '{selected_size}' is not valid")
        #     return JsonResponse({'error': 'Invalid size selected'}, status=400)

        # Create a new Product instance with the received color and size
        product = Product.objects.create(
            colour=selected_color,
            size=selected_size,
            product_type='t-shirt'
        )

        # Get the customer and order
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Create an OrderItem with the new product and order
        order_item = OrderItem.objects.create(
            product=product,
            order=order
        )

        # Log a success message
        print("Product added to cart successfully")

        # Return a JSON response indicating success
        return JsonResponse({'message': 'Product added to cart successfully'}, status=200)
    else:
        # Log a message indicating that the request method is not POST
        print("Request method is not POST")

        # Return an appropriate response, such as a JSON response with an error message
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')

        # Check if the product ID is provided
        if not product_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)

        try:
            # Get the OrderItem to be removed based on the product ID
            order_item = OrderItem.objects.get(product_id=product_id, order__customer=request.user.customer)
            order_item.delete()  # Remove the OrderItem from the cart
            order_item.product.delete()

            # Log a success message
            print("Product removed from cart successfully")

            # Return a JSON response indicating success
            return JsonResponse({'message': 'Product removed from cart successfully'}, status=200)
        except OrderItem.DoesNotExist:
            # If the OrderItem does not exist, return an error response
            return JsonResponse({'error': 'Product not found in cart'}, status=404)
    else:
        # If the request method is not POST, return an error response
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    
