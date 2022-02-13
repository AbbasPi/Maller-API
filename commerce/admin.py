from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from easy_select2 import select2_modelform
from mptt.admin import DraggableMPTTAdmin
from nested_inline.admin import NestedModelAdmin, NestedStackedInline

from commerce.models import Product, Order, Item, Address, OrderStatus, ProductImage, City, Category, Merchant, \
    Label, ProductRating, VendorRating, Promo, DeliveryMap

User = get_user_model()

admin.site.site_header = 'Maller'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = select2_modelform(City)
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 10


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    form = select2_modelform(Address)
    list_display = (
        'user',
        'work_address',
        'address1',
        'address2',
        'city',
        'phone',
    )
    list_filter = ('user', 'work_address', 'city')


class TabularItem(admin.TabularInline):
    model = Order.items.through
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TabularItem]
    form = select2_modelform(Order)
    list_display = (
        'user',
        'id',
        'total',
        'status',
        'note',
        'ref_code',
        'ordered',
        'promo',
        'shipping',
    )
    list_filter = ('user', 'status', 'promo', 'ordered', 'ref_code')

    fieldsets = (
        ('order', {'fields': (
            'user',
            'total',
            'status',
            'note',
            'ref_code',
            'ordered',
            'promo',
            'address',
            'items',
            'shipping',
        ), 'classes': 'wide'}),
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    form = select2_modelform(Item)
    list_display = ('product', 'item_qty', 'ordered')
    list_filter = ('product', 'ordered')


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_default')
    list_filter = ('is_default',)


@admin.register(DeliveryMap)
class DeliveryMapAdmin(admin.ModelAdmin):
    form = select2_modelform(DeliveryMap)
    list_display = ('source', 'destination', 'cost')
    list_filter = ('cost',)


class TabularProductImage(admin.TabularInline):
    model = ProductImage
    inlines = []
    extra = 9


@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    inlines = [TabularProductImage]
    form = select2_modelform(Product)
    list_display = (
        'name',
        'pk',
        'slug',
        'category',
        'merchant',
        'is_featured',
        'is_active',
        'label'
    )
    list_filter = (
        'category',
        'merchant',
        'vendor',
        'is_featured',
        'is_active',
        'label',
    )
    search_fields = ('name', 'slug')
    list_per_page = 10

    fieldsets = (
        ('general information', {'fields': ('name', 'slug')}),
        ('data', {'fields': ('description', 'weight', 'width', 'height', 'length')}),
        (
            'pre-populated', {
                'fields': (
                    'lowest', 'lowest_discounted', 'qty', 'is_featured', 'is_active', 'vendor', 'category', 'label',
                    'merchant'
                )
            }),

    )


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    # inlines = [TabularCategoryTranslation]
    mptt_indent_field = "name"
    form = select2_modelform(Category)
    list_display = (
        'indented_title',
        'id',
        'parent',
        'description',
        'cat_image',
        'is_active',
        'related_products_count',
        'related_products_cumulative_count'
    )
    list_display_links = ('indented_title',)
    list_filter = ('parent', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ['name']}

    def cat_image(self, obj):
        return mark_safe('<img src="{url}" width="50" height="50" />'.format(
            url=obj.image.url,
        )
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Add cumulative product count
        qs = Category.objects.add_related_count(
            qs,
            Product,
            'category',
            'products_cumulative_count',
            cumulative=True)

        # Add non cumulative product count
        qs = Category.objects.add_related_count(qs,
                                                Product,
                                                'category',
                                                'products_count',
                                                cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count

    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count

    related_products_cumulative_count.short_description = 'Related products (in tree)'


@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    form = select2_modelform(Merchant)
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    form = select2_modelform(ProductImage)
    list_display = ('image', 'alt_text', 'is_default_image', 'product')
    list_filter = ('is_default_image', 'product')

    fieldsets = (
        ('data', {'fields': ('image', 'alt_text', 'is_default_image'), }),

    )


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    # inlines = [TabularLabelTranslation]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    form = select2_modelform(Promo)
    list_display = (
        'name',
        'code',
        'description',
        'is_active',
        'type',
        'amount',
        'active_from',
        'active_till',
    )
    list_filter = ('is_active', 'active_from', 'active_till')
    search_fields = ('name',)





@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'rate', 'user')
    search_fields = ('rate', 'product', 'user')


admin.site.register(VendorRating)
