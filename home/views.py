from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.core.files.storage import FileSystemStorage
from .forms import SellerProfileForm
from django.http import JsonResponse
import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from .forms import ReviewForm



def cart_show_pages(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    cart_item_count = items.count() 
    return cart, items, total, cart_item_count

from django.db.models import Q

def home(request):
    # NEW: Only show recently created products (last 20 products)
    products = Product.objects.all().order_by('-created_at')[:20]

    # Unique categories nikal lo
    unique_categories = Product.objects.values_list('category', flat=True).distinct()
    
    # Unique categories wale products (top categories section ke liye)
    category_products = []
    for category in unique_categories:
        # Har category ka pehla product le lo
        product = Product.objects.filter(category=category).first()
        if product:
            category_products.append(product)

    # SIMPLE APPROACH: List of dictionaries banaye
    categories_with_products = []
    for category in unique_categories:
        # NEW: Category products bhi latest first
        category_products_list = Product.objects.filter(category=category).order_by('-created_at')[:8]
        if category_products_list:
            categories_with_products.append({
                'name': category,
                'products': category_products_list
            })

    if request.user.is_authenticated:
        cart, items, total, cart_item_count = cart_show_pages(request)
    else:
        cart = items = total = cart_item_count = None
    
    if request.GET.get('search'):
        search = request.GET.get('search')
        
        # Price ko numeric check karke alag se filter
        try:
            price_search = float(search)
            products = Product.objects.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search) |
                Q(seller__user__username__icontains=search) |
                Q(price=price_search)
            ).order_by('-created_at')
        except ValueError:
            products = Product.objects.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search) |
                Q(seller__user__username__icontains=search)
            ).order_by('-created_at')
    
    return render(request, 'home.html', {
        'products': products, 
        'category_products': category_products,
        'categories_with_products': categories_with_products,
        'selected_category': None,
        'cart': cart, 
        'items': items, 
        'total': total, 
        'cart_item_count': cart_item_count 
    })



def category_products(request, category_name):
    # Specific category ke products filter karo
    products = Product.objects.filter(category__iexact=category_name)
    
    # Unique categories for top section
    unique_categories = Product.objects.values_list('category', flat=True).distinct()
    category_products_list = []
    for category in unique_categories:
        product = Product.objects.filter(category=category).first()
        if product:
            category_products_list.append(product)
    
    if request.user.is_authenticated:
        cart, items, total, cart_item_count = cart_show_pages(request)
    else:
        cart = items = total = cart_item_count = None
    
    context = {
        'products': products,
        'category_products': category_products_list,
        'selected_category': category_name,
        'cart': cart, 
        'items': items, 
        'total': total, 
        'cart_item_count': cart_item_count
    }
    return render(request, 'home.html', context)


@login_required(login_url='/accounts/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })

@login_required(login_url='/accounts/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if created:
        cart_item.quantity = 1
    else:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')

@login_required(login_url='/accounts/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('cart')

@login_required(login_url='/accounts/login/')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        if quantity:
            cart_item.quantity = int(quantity)
            cart_item.save()
    return redirect('cart')




@login_required
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    items = cart.items.all()

    if request.method == "POST":
        order = Order.objects.create(user=request.user)

        for item in items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            # Seller email
            seller_email = item.product.seller.user.email
            send_mail(
                subject="New Order Received - G-Mart",
                message=f"You got an order!\nProduct: {item.product.name}\nQuantity: {item.quantity}\nBuyer: {request.user.username}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[seller_email],
                fail_silently=False,
            )

        # Buyer email
        send_mail(
            subject="Order Confirmation - G-Mart",
            message=f"Hello {request.user.username},\nYour order #{order.id} has been placed successfully!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        cart.items.all().delete()  # Clear cart
        return redirect('order_success')

    total = sum(item.product.price * item.quantity for item in items)
    return render(request, 'checkout.html', {'items': items, 'total': total, 'cart': cart, 'cart_item_count': cart_item_count })


@login_required(login_url='/accounts/login/')
def order_history(request):
    orders = Order.objects.filter(buyer__user=request.user).order_by('-created_at')
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    return render(request, 'order_history.html', {'orders': orders, 'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })

@login_required(login_url='/accounts/login/')
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, buyer__user=request.user)
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    if request.method == 'POST':
        order.delete()
        return redirect('order_history')
    return render(request, 'confirm_delete.html', {'order': order, 'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })



@login_required(login_url='/accounts/login/')
def place_order(request):
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")          # buyer email
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        # ✅ Order Save in DB
        order = Order.objects.create(
            customer_name=full_name,
            customer_email=email,
            customer_phone=phone,
            shipping_address=address,
            payment_method=payment_method,
            status="Pending"
        )

        # ✅ Cart ke products ko OrderItem me save karo (example)
        cart = request.session.get("cart", [])
        for item in cart:
            product = Product.objects.get(id=item["id"])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["qty"],
                price=product.price,
            )

        # ==================================
        # 🔔 Notifications
        # ==================================

        # Buyer Email
        send_mail(
            subject="Order Confirmation - G-Mart",
            message=f"Hello {full_name},\n\nThank you for your order!\nYour order #{order.id} has been received.\n\nRegards,\nG-Mart",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        # Seller Email (yaha seller ka email DB se nikalna hai)
        seller_email = "seller@example.com"  # abhi hardcoded, baad me SellerProfile se fetch karna
        send_mail(
            subject="New Order Received - G-Mart",
            message=f"Hello Seller,\n\nYou have received a new order from {full_name}.\nOrder ID: {order.id}\nCustomer Email: {email}\nCustomer Phone: {phone}\n\nCheck your dashboard for details.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[seller_email],
            fail_silently=False,
        )

        # ✅ Clear cart after order
        request.session["cart"] = []

        messages.success(request, "Your order has been placed successfully!")
        return redirect("order_success")

    return render(request, "checkout.html", {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })


# seller acount loing logout regiser 
def seller_register(request):
    if request.user.is_authenticated:
        cart, items, total, cart_item_count = cart_show_pages(request)
    else:
        cart = items = total = cart_item_count = None
    """Seller registration form page show karega"""
    return render(request, "seller_register.html", {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })



def seller_register_submit(request):
    """Seller registration form submit handle karega"""
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        store_name = request.POST.get("store_name")
        business_type = request.POST.get("business_type")
        tax_id = request.POST.get("tax_id")
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")
        country = request.POST.get("country")
        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        ifsc = request.POST.get("ifsc")
        payment_email = request.POST.get("payment_email")

        identity_proof = request.FILES.get("identity_proof")
        business_document = request.FILES.get("business_document")

        # Password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("seller_registration")

        # Email unique check
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("seller_registration")

        # Create User
        user = User.objects.create_user(username=email, email=email, password=password, first_name=full_name)
        user.save()

        # Save seller profile
        seller = SellerProfile.objects.create(
            user=user,
            store_name=store_name,
            business_type=business_type,
            tax_id=tax_id,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            bank_name=bank_name,
            account_number=account_number,
            ifsc=ifsc,
            payment_email=payment_email,
            status="pending",  # admin approve karega
        )

        # Save uploaded files
        if identity_proof:
            fs = FileSystemStorage()
            seller.identity_proof = fs.save(identity_proof.name, identity_proof)
        if business_document:
            fs = FileSystemStorage()
            seller.business_document = fs.save(business_document.name, business_document)
        
        seller.save()

        messages.success(request, "Seller account created! Please wait for admin approval.")
        return redirect("seller_login")

    return redirect("seller_registration")


def seller_register_submit(request):
    if request.method == "POST":
        # Email validation
        email = request.POST.get("email")
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address")
            return redirect("seller_register")
        
        # Password validation
        password = request.POST.get("password")
        if len(password) < 8 or not re.search(r"[A-Z]", password) or not re.search(r"[a-z]", password) or not re.search(r"[0-9]", password):
            messages.error(request, "Password must be at least 8 characters with uppercase, lowercase, and number")
            return redirect("seller_register")
        
        # IFSC validation
        ifsc = request.POST.get("ifsc")
        ifsc_pattern = re.compile(r'^[A-Z]{4}0[A-Z0-9]{6}$')
        if not ifsc_pattern.match(ifsc.upper()):
            messages.error(request, "Please enter a valid IFSC code")
            return redirect("seller_register")
        
        # File validation
        identity_proof = request.FILES.get("identity_proof")
        if identity_proof:
            if identity_proof.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, "File size too large. Maximum 5MB allowed")
                return redirect("seller_register")
            
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
            if identity_proof.content_type not in allowed_types:
                messages.error(request, "Invalid file type. Please upload PDF, JPG, or PNG")
                return redirect("seller_register")
        



def seller_login(request):
    """Seller login view"""
    if request.user.is_authenticated:
        cart, items, total, cart_item_count = cart_show_pages(request)
    else:
        cart = items = total = cart_item_count = None
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Welcome Seller!")
            return redirect("/")  # seller dashboard bana ke yaha redirect kar sakte ho
        else:
            messages.error(request, "Invalid credentials!")
            return redirect("seller_login")

    return render(request, "seller_login.html", {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })


# term and condition page 
@login_required(login_url='/accounts/login/')
def terms(request):
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    return render(request, "terms.html", {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })


# buyser

def buyer_register(request):
    if request.user.is_authenticated:
        cart, items, total, cart_item_count = cart_show_pages(request)
    else:
        cart = items = total = cart_item_count = None
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        user = User.objects.create_user(username=username, email=email, password=password)
        BuyerProfile.objects.create(user=user)  # blank profile
        login(request, user)
        return redirect("home")
    return render(request, "buyer_register.html", {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })


# checkout 
@login_required(login_url='/accounts/login/')
def checkout(request):
    cart = Cart.objects.get(user=request.user)
    buyer_profile = BuyerProfile.objects.get(user=request.user)

    # Order create
    order = Order.objects.create(
        buyer=buyer_profile,
        payment_method="cod"
    )

    # Order items
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    # Buyer email
    send_mail(
        "Order Confirmation",
        f"Hello {buyer_profile.user.username},\nYour order #{order.id} has been placed successfully.",
        settings.DEFAULT_FROM_EMAIL,
        [buyer_profile.user.email],
        fail_silently=False,
    )

    # Seller email
    for item in order.items.all():
        send_mail(
            "New Order Received",
            f"You have a new order for {item.product.name}, Quantity: {item.quantity}",
            settings.DEFAULT_FROM_EMAIL,
            [item.product.seller.user.email],
            fail_silently=False,
        )

    # Empty cart after checkout
    cart.items.all().delete()

    return redirect("order_success")


# contect page
@login_required(login_url='/accounts/login/')
def contact(request):
    cart, items, total, cart_item_count = cart_show_pages(request)  # <-- assign values
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        # Save to DB
        Contact.objects.create(fullname=name, email=email, subject=subject , message=message)

        # Send email to admin
        # send_mail(
        #     subject=f"New Contact Message from {name}",
        #     message=message,
        #     from_email=email,
        #     recipient_list=[settings.DEFAULT_FROM_EMAIL],
        #     fail_silently=False,
        # )

        messages.success(request, "Your message has been sent!")
        return redirect("contact")

    return render(request, "contact.html", {'cart': cart, 'items': items, 'total': total, 'cart_item_count': cart_item_count })





# profile views start right here


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = request.user

    # check if seller hai
    if hasattr(user, 'sellerprofile'):
        seller = user.sellerprofile
        products = Product.objects.filter(seller=seller)
        return render(request, "profile_seller.html", {"seller": seller, "products": products})
    
    # otherwise buyer
    return render(request, "profile_buyer.html", {"buyer": user})



@login_required(login_url='/accounts/login/')
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    # Check if user has already reviewed this product
    user_review = None
    if request.user.is_authenticated:
        try:
            user_review = Review.objects.get(product=product, user=request.user)
        except Review.DoesNotExist:
            pass
    
    context = {
        'product': product,
        'user_review': user_review,
    }
    return render(request, 'product_detailed.html', context)

@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, 'You have already reviewed this product.')
        return redirect('product_detail', pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            # Handle multiple images
            images = request.FILES.getlist('review_images')
            for image in images[:4]:  # Limit to 4 images
                ReviewImage.objects.create(review=review, image=image)
            
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('product_detail', pk=pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()
    
    return render(request, 'product_detail.html', {'product': product, 'form': form})

@login_required
@require_POST
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check if user owns the review
    if review.user != request.user:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    review.delete()
    return JsonResponse({'success': True})





# create product notification
def create_product_notification(product):
    """New product add hone par sabhi users ko notification bheje"""
    from django.contrib.auth.models import User
    
    users = User.objects.all()
    notifications = []
    
    for user in users:
        notification = Notification(
            user=user,
            notification_type='new_product',
            title='New Product Added!',
            message=f'{product.seller.store_name} added a new product: {product.name}',
            product=product
        )
        notifications.append(notification)
    
    # Bulk create for better performance
    Notification.objects.bulk_create(notifications)






@login_required(login_url='/accounts/login/')
def add_product(request):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('seller_registration')
    
    existing_categories = Product.objects.values_list('category', flat=True).distinct()
    
    if request.method == 'POST':
        try:
            name = request.POST.get('pname')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            category = request.POST.get('category') or request.POST.get('new_category')
            description = request.POST.get('description')
            available = request.POST.get('available') == 'on'
            
            # Create new product
            product = Product.objects.create(
                seller=request.user.sellerprofile,
                name=name,
                price=price,
                stock=stock,
                category=category,
                description=description,
                available=available
            )
            
            # Handle multiple images - CORRECTED
            images = request.FILES.getlist('images')
            for image in images:
                if image:  # Check if image is not empty
                    Prod_Image.objects.create(prod=product, image=image)

            # 🔔 NOTIFICATION CREATE KAREIN
            create_product_notification(product)
            
            messages.success(request, 'Product added successfully!')
            return redirect('profile')
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    context = {
        'existing_categories': existing_categories
    }
    return render(request, 'product_form.html', context)



@login_required
def all_notifications(request):
    notifications = request.user.notifications.all()
    cart, items, total, cart_item_count = cart_show_pages(request)
    
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'cart': cart,
        'items': items,
        'total': total,
        'cart_item_count': cart_item_count
    })




@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('all_notifications')

@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('all_notifications')

@login_required
def get_unread_count(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
        return JsonResponse({'count': count})
    return JsonResponse({'count': 0})

# Real-time notifications ke liye API
@login_required
def get_recent_notifications(request):
    notifications = request.user.notifications.all()[:5]
    data = []
    
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'product_url': notification.product.get_absolute_url() if notification.product else '#',
            'type': notification.notification_type
        })
    
    return JsonResponse({'notifications': data})



@login_required(login_url='/accounts/login/')
def edit_product(request, product_id):
    if not hasattr(request.user, 'sellerprofile'):
        return redirect('seller_registration')
    
    product = get_object_or_404(Product, id=product_id, seller=request.user.sellerprofile)
    existing_categories = Product.objects.values_list('category', flat=True).distinct()
    
    if request.method == 'POST':
        try:
            name = request.POST.get('pname')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            category = request.POST.get('category') or request.POST.get('new_category')
            description = request.POST.get('description')
            available = request.POST.get('available') == 'on'
            
            # Update existing product
            product.name = name
            product.price = price
            product.stock = stock
            product.category = category
            product.description = description
            product.available = available
            product.save()
            
            # Handle new images - CORRECTED
            images = request.FILES.getlist('images')
            for image in images:
                if image:  # Check if image is not empty
                    Prod_Image.objects.create(prod=product, image=image)
            
            messages.success(request, 'Product updated successfully!')
            return redirect('profile')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    context = {
        'product': product,
        'existing_categories': existing_categories
    }
    return render(request, 'product_form.html', context)


# Add this view for removing images
def remove_product_image(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(Prod_Image, id=image_id)
        # Check if the image belongs to user's product
        if image.prod.seller.user == request.user:  # 'prod' use karo
            image.delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})




@login_required(login_url='/accounts/login/')
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user.sellerprofile)
    product.delete()
    return redirect('profile')



# edit seller profile 
@login_required(login_url='/accounts/login/')
def edit_seller_profile(request):
    seller = request.user.sellerprofile
    if request.method == "POST":
        form = SellerProfileForm(request.POST, request.FILES, instance=seller)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = SellerProfileForm(instance=seller)
    return render(request, "edit_seller_profile.html", {"form": form, "seller": seller})