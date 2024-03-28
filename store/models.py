from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# OneToOneFeild() means a user can have only one customer and a customer has only one user
# on_delete=models.CASCADE use to delete the item if we delete user item
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    name = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=100, null=True)

    # this value will show in the admin panel when we create the model
    def __str__(self):
        return self.name
    
class Product(models.Model):
    SIZES = {
        "XS": "Extra Small",
        "S": "Small",
        "M": "Medium",
        "L": "Large",
        "XL": "Extra Large",
        "XXL": "Double Extra Large",
    }
    TYPES = {
        "t-shirt": "T-Shirt",
        "hoodie": "Hoodie",
    }
    COLOURS = {
        "white": "White",
        "black": "Black",
        "off-white": "Off-White",
        "red": "Red",
        "brown": "Brown",
        "green": "Green",
        "yellow": "Yellow",
        "pink": "Pink",
    }
    product_type = models.CharField(max_length=10, choices=TYPES, default='t-shirt')
    name = models.CharField(max_length=50, null=True, blank=True)
    price = models.IntegerField(default=1999)
    colour = models.CharField(max_length=10, choices=COLOURS, default='off-white')
    image = models.ImageField(null=True, blank=True)
    size = models.CharField(max_length=3, choices=SIZES, default='L')
    

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
    # Set price based on product type
        if self.product_type == 't-shirt':
            self.price = 1999
            self.name = 't-shirt'
        elif self.product_type == 'hoodie':
            self.price = 3999
            self.name = 'hoodie'
        super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

# ForeignKey is used to create many to one relationship i.e a customer can have multiple orders
# on_delete=models.SET_NULL is used for if the user is deleted we don't have to delete the order, just have to set the value of user to null
# if complete is false this means the cart is open and we can continue adding items in the cart
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
    
    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([1 for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price
        return total


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=300, null=False)
    city = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    zipcode = models.IntegerField(null=False)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.address
    
