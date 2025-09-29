from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# seller profile account
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    ifsc = models.CharField(max_length=20)
    payment_email = models.CharField(max_length=150, blank=True, null=True)
    identity_proof = models.FileField(upload_to="seller_docs/", blank=True, null=True)
    business_document = models.FileField(upload_to="seller_docs/", blank=True, null=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    brand_image = models.ImageField(upload_to='brand_images/', blank=True, null=True)  # Brand image field

    def __str__(self):
        return f"{self.store_name} - {self.user.username} - {self.status}"
    

# Product Model
class Product(models.Model):
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, default=1 )  # seller relation
    name = models.CharField(max_length=255)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=500,default='Other')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    # Add this property for average rating
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    # Add this property for review count
    @property
    def review_count(self):
        return self.reviews.count()
    

class Prod_Image(models.Model):
    prod = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prod_images')
    image = models.ImageField(upload_to='prod')

    def __str__(self):
        return f"{self.prod.name} Image"


# Review System Models - ADD THESE NEW MODELS
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        choices=((1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars'))
    )
    title = models.CharField(max_length=200, blank=True, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']  # One review per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} Stars"


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.review.product.name}"


class ProdBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fullname = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField()
    datetime = models.DateTimeField(auto_now_add=True)
    destination = models.CharField(max_length=300)
    message = models.TextField()

    def __str__(self):
        return self.fullname +'--'+ self.email
    

class Contact(models.Model):
    fullname = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200)
    datetime = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return self.fullname +'--'+ self.email
    

# Cart Model
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

# Cart Item Model
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Ensure a default value

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def total_price(self):
        return self.quantity * self.product.price

# Order Model

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Buyer: {self.user.username}"

class Order(models.Model):
    buyer = models.ForeignKey(BuyerProfile, on_delete=models.CASCADE , default=1)  # buyer relation
    payment_method = models.CharField(max_length=50, choices=(("cod","Cash on Delivery"),("online","Online Payment")), default="cod")
    status = models.CharField(max_length=50, default="Pending")  # Pending, Shipped, Delivered
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.buyer.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    




# Notification Model
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_product', 'New Product'),
        ('new_order', 'New Order'),
        ('price_drop', 'Price Drop'),
        ('promotion', 'Promotion'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    