from django.contrib import admin

from commerce.models import Product, Order, Item, Address, OrderStatus, ProductImage, City, Category, Merchant, \
    Label, ProductRating, VendorRating


class InlineProductImage(admin.TabularInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    inlines = [InlineProductImage, ]
    list_display = ('id', 'name', 'qty', 'description', 'cost', 'price', 'discounted_price', 'vendor')
    list_filter = ('category', 'label', 'merchant', 'vendor')
    search_fields = ('name', 'qty', 'description', 'cost', 'price', 'discounted_price', 'merchant__name')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class LabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class MerchantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Product, ProductAdmin)
admin.site.register(Order)
admin.site.register(Item)
admin.site.register(Address)
admin.site.register(OrderStatus)
admin.site.register(City)
admin.site.register(Category, MerchantAdmin)
admin.site.register(Merchant, MerchantAdmin)
admin.site.register(Label, LabelAdmin)
admin.site.register(ProductRating)
admin.site.register(VendorRating)
