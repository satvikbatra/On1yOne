from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
# from .models import SIZES
import datetime
import requests
from django.conf import settings
import os

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
        print("Items:", items)
    else:
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        items = []
    context = {'items': items, 'order': order}
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
        tshirt_back_image = data.get('tshirt_back_image')  # Retrieve back image URL
        prod_design_image = data.get('design_image')

        # Create or get the Product instance
        product, created = Product.objects.get_or_create(
            product_type='t-shirt',  # Replace with actual product type
            name='Your T-Shirt Product Name',  # Replace with actual product name
            colour=selected_color,
            size=selected_size,
            defaults={'image': tshirt_back_image, 'design': prod_design_image}  # Set default values
        )

        # Get or create the Order and associate it with the customer
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        # Create an OrderItem with the new product and order
        order_item = OrderItem.objects.create(
            product=product,
            order=order
        )

        # Return a JSON response indicating success
        return JsonResponse({'message': 'Product added to cart successfully'}, status=200)
    else:
        # Return an appropriate response if the request method is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def add_to_cart_hoodie(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_color = data.get('color')
        selected_size = data.get('size')
        hoodie_back_image = data.get('hoodie_back_image')
        prod_design_image = data.get('design_image')

        product, created = Product.objects.get_or_create(
            product_type='hoodie',  # Replace with actual product type
            name='Your Hoodie Product Name',  # Replace with actual product name
            colour=selected_color,
            size=selected_size,
            defaults={'image': hoodie_back_image, 'design': prod_design_image}  # Set default values
            # design_image = prod_design_image
        )

        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        order_item = OrderItem.objects.create(
            product=product,
            order=order
        )

        return JsonResponse({'message': 'Product added to cart successfully'}, status=200)
    else:
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
    
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
            
        order.save()

        
        ShippingAddress.objects.create(
        customer=customer,
        order=order,
        address=data['shipping']['address'],
        city=data['shipping']['city'],
        state=data['shipping']['state'],
        zipcode=data['shipping']['zipcode'],
        )
            

    return JsonResponse('payment complete', safe=False)



def generate_image_tshirt(request):
    api_url = 'http://127.0.0.1:8000/get_image'

    response = requests.get(api_url)

    if response.status_code == 200:
        generated_image_bytes = response.content

        image_dir = settings.STATIC_ROOT
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        image_path = os.path.join(image_dir, 'generated_image.jpg')

        with open(image_path, 'wb') as f:
            f.write(generated_image_bytes)

        return redirect('t-shirt')
    else:
        return JsonResponse("Error: Unable to generate image", status=response.status_code, safe=False)
    

def generate_image_hoodie(request):
    api_url = 'http://127.0.0.1:8000/get_image'

    response = requests.get(api_url)

    if response.status_code == 200:
        generated_image_bytes = response.content

        image_dir = settings.STATIC_ROOT
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        image_path = os.path.join(image_dir, 'generated_image1.jpg')

        with open(image_path, 'wb') as f:
            f.write(generated_image_bytes)

        return redirect('hoodie')
    else:
        return JsonResponse("Error: Unable to generate image", status=response.status_code, safe=False)