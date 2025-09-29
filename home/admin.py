from django.contrib import admin
from .models import *

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(SellerProfile)
admin.site.register(ProdBooking)
admin.site.register(Contact)

class ProdImageAdmin(admin.StackedInline):
    model = Prod_Image

class ProdAdmin(admin.ModelAdmin):
    inlines = [ProdImageAdmin]

admin.site.register(Product,ProdAdmin)
admin.site.register(Prod_Image)
admin.site.register(Review)
admin.site.register(ReviewImage)
admin.site.register(BuyerProfile)
admin.site.register(Notification)