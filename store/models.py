from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import os

def unique_design_image_path(instance, filename):
    """
    Generate a unique file path for design images.
    """
    ext = filename.split('.')[-1]
    unique_filename = f"design_{uuid.uuid4().hex}.{ext}"
    return os.path.join('static', 'images', unique_filename)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    name = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.name

# Signal to create a Customer instance whenever a new User is created
@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

# Signal to save the Customer instance whenever the related User instance is saved
@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()  # Ensure the corresponding Customer instance is saved whenever the related User is saved

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
    design = models.ImageField(upload_to=unique_design_image_path, null=True, blank=True)  # Updated upload_to
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
    
    @property
    def designURL(self):
        try:
            url = self.design.url
        except:
            url = ""
        return url




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
        if self.product:
            total = self.product.price
        else:
            total = 0
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
