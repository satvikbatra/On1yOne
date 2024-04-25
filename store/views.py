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
from django.conf import settings # new
from django.http.response import JsonResponse # new
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.contrib.auth import logout


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

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
    

def home(request):
    context = {}
    return render(request, 'store/home.html', context)

@login_required
def store_t_shirt(request):
    context = {}
    return render(request, 'store/store_tshirt.html', context)

@login_required
def store_hoodie(request):
    context = {}
    return render(request, 'store/store_hoodie.html', context)

@login_required
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


@login_required
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

import os
import uuid

import requests

def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Received data:", data) 
        selected_color = data.get('color')
        selected_size = data.get('size')
        tshirt_back_image = data.get('tshirt_back_image') 
        prod_design_image_url = data.get('design_image') 
        
        if not prod_design_image_url.startswith(('http://', 'https://')):
            prod_design_image_url = request.scheme + '://' + request.get_host() + prod_design_image_url
        
        try:
            response = requests.get(prod_design_image_url)
            response.raise_for_status()
            prod_design_image = response.content
        except requests.exceptions.RequestException as e:
            error_message = f"Error retrieving design image: {e}"
            print(error_message)
            return JsonResponse({'error': error_message}, status=400)
        
        unique_filename = f"design_{uuid.uuid4().hex}.jpg"

        image_path = os.path.join('static', 'images', unique_filename)
        with open(image_path, 'wb') as f:
            f.write(prod_design_image)

        product, created = Product.objects.get_or_create(
            product_type='t-shirt',
            name='Your T-Shirt Product Name',
            colour=selected_color,
            size=selected_size,
            defaults={'image': tshirt_back_image, 'design': image_path}
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



def add_to_cart_hoodie(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print("Received data:", data) 
        selected_color = data.get('color')
        selected_size = data.get('size')
        hoodie_back_image = data.get('hoodie_back_image') 
        prod_design_image_url = data.get('design_image') 
        
        if not prod_design_image_url.startswith(('http://', 'https://')):
            prod_design_image_url = request.scheme + '://' + request.get_host() + prod_design_image_url
        
        try:
            response = requests.get(prod_design_image_url)
            response.raise_for_status()
            prod_design_image = response.content
        except requests.exceptions.RequestException as e:
            error_message = f"Error retrieving design image: {e}"
            print(error_message)
            return JsonResponse({'error': error_message}, status=400)
        
        unique_filename = f"design_{uuid.uuid4().hex}.jpg"

        image_path = os.path.join('static', 'images', unique_filename)
        with open(image_path, 'wb') as f:
            f.write(prod_design_image)

        product, created = Product.objects.get_or_create(
            product_type='hoodie',
            name='Your Hoodie Product Name',
            colour=selected_color,
            size=selected_size,
            defaults={'image': hoodie_back_image, 'design': image_path}
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



@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

from django.db.models import Sum


stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:2222/checkout/'  # Update with your domain URL
        try:
            # Calculate cart total
            # cart_total = OrderItem.objects.aggregate(total=Sum('product__price'))['total']
            order = Order.objects.get(customer=request.user.customer, complete=False)
            cart_total = order.get_cart_total()

            # Retrieve customer name and address from the request (modify this part based on how you collect this information)
            customer_name = request.GET.get('customer_name')
            customer_address = request.GET.get('customer_address')

            # Create a new checkout session with customer name and address
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                customer_email=request.user.email,  # Assuming you have authenticated users and you want to use their email
                line_items=[{
                    'price_data': {
                        'currency': 'inr',
                        'product_data': {
                            'name': 'Cart Total',
                        },
                        'unit_amount': int(cart_total * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                shipping_address={
                    'name': customer_name,
                    'address': {
                        'line1': customer_address,
                    },
                }
            )
            return JsonResponse({'sessionId': checkout_session['id'], 'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY})
        except Exception as e:
            return JsonResponse({'error': str(e)})