from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('store/t_shirt', views.store_t_shirt, name='t-shirt'),
    path('store/hoodie', views.store_hoodie, name='hoodie'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update-cart/', views.update_cart, name='update-cart'),
    path('process-order/', views.processOrder, name='process-order'),
    path('add-to-cart-hoodie/', views.add_to_cart_hoodie, name='add-to-cart-hoodie'),
    path('generate_image_tshirt/', views.generate_image_tshirt, name='generate_image_tshirt'),
    path('generate_image_hoodie/', views.generate_image_hoodie, name='generate_image_hoodie'),

]

