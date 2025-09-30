from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', home, name='home'),
    path('category/<str:category_name>/', category_products, name='category_products'),

    # cart url 
    path('cart/', cart_view, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', update_cart_item, name='update_cart_item'),
    path('checkout/', checkout_view, name='checkout'),
    path('order-success/', order_success, name='order_success'),

    # order url 
    path('orders/', order_history, name='order_history'),
    path('orders/delete/<int:order_id>/', delete_order, name='delete_order'),

    # seller url
    path("seller/register/", seller_register, name="seller_registration"),
    path("seller/register/submit/",seller_register_submit, name="seller_register_submit"),
    path("seller/login/", seller_login, name="seller_login"),

    
    # terms & conditions
    path("terms/", terms, name="terms"),

    # buyer
    path("buyer/register/", buyer_register, name="buyer_register"),
    path("buyer/login/", auth_views.LoginView.as_view(template_name="buyer_login.html"), name="buyer_login"),
    path("buyer/logout/", auth_views.LogoutView.as_view(next_page="home"), name="buyer_logout"),
    # path("buyer/dashboard/", buyer_dashboard, name="buyer_dashboard"),

    # contact url
    path("contact/", contact, name="contact"),

    # profile urls 
    path("profile/", profile_view, name="profile"),
    path("product/add/", add_product, name="add_product"),
    # Change pk to product_id
    path('product/<int:product_id>/edit/', edit_product, name='edit_product'),
    path("product/<int:pk>/delete/", delete_product, name="delete_product"),

    # edit seller profile
    path("profile/seller/edit/", edit_seller_profile, name="edit_seller_profile"),

    # product details 
    path('product/<int:pk>/', product_detail, name='product_detail'),

    # add product image remove path 
    path('remove-product-image/<int:image_id>/', remove_product_image, name='remove_product_image'),

    # reveiws and ratings 
    path('product/<int:pk>/review/', add_review, name='add_review'),
    path('reviews/<int:review_id>/delete/', delete_review, name='delete_review'),

    # Notification URLs
    path('notifications/', all_notifications, name='all_notifications'),
    path('notifications/mark-read/<int:notification_id>/', mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', mark_all_read, name='mark_all_read'),
    path('notifications/unread-count/', get_unread_count, name='get_unread_count'),
    path('notifications/recent/', get_recent_notifications, name='get_recent_notifications'),


]

# username = root
# password = root