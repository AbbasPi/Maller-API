import uuid
from PIL import Image
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from taggit.managers import TaggableManager

from config.utils.models import Entity

User = get_user_model()


class Product(Entity):
    name = models.CharField('name', max_length=255)
    slug = models.SlugField('slug', default=uuid.uuid4, unique=True)
    description = RichTextField('description', null=True, blank=True)
    qty = models.DecimalField('qty', max_digits=10, decimal_places=2)
    weight = models.FloatField('weight', null=True, blank=True)
    width = models.FloatField('width', null=True, blank=True)
    height = models.FloatField('height', null=True, blank=True)
    length = models.FloatField('length', null=True, blank=True)
    lowest = models.DecimalField('lowest', max_digits=10, decimal_places=2)
    lowest_discounted = models.DecimalField('lowest_discounted', max_digits=10, decimal_places=2)
    vendor = models.ForeignKey('account.Vendor', verbose_name='vendor', related_name='products',
                               on_delete=models.CASCADE)
    category = models.ForeignKey('commerce.Category', verbose_name='category', related_name='products',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    merchant = models.ForeignKey('commerce.Merchant', verbose_name='merchant', related_name='products',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    is_featured = models.BooleanField('is featured')
    is_active = models.BooleanField('is active')
    label = models.ForeignKey('commerce.Label', verbose_name='label', related_name='products', null=True, blank=True,
                              on_delete=models.CASCADE)

    tags = TaggableManager()

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name

    @property
    def in_stock(self):
        return self.qty > 0

    @property
    def average_rating(self):
        rating_sum = sum(i.rate for i in self.product_rating.all())
        rating_count = self.product_rating.count()
        if rating_count == 0:
            return 0
        average_rating = rating_sum / rating_count
        return average_rating

    @property
    def images(self):
        return self.images.all()


class ProductImage(Entity):
    image = models.ImageField('image', upload_to='product/')
    alt_text = models.CharField('alt text', null=True, blank=True, max_length=255)
    is_default_image = models.BooleanField('is default image')
    product = models.ForeignKey('commerce.Product', verbose_name='product', related_name='images',
                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'product image'
        verbose_name_plural = 'product images'

    def __str__(self):
        return str(self.product.name)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 500 or img.width > 500:
            output_size = (500, 500)
            img.thumbnail(output_size)
            img.save(self.image.path)


class ProductRating(Entity):
    rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True,
                             blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_rating')
    user = models.ForeignKey(User, related_name='product_rating', on_delete=models.CASCADE)

    def __int__(self):
        return self.product.name


class Merchant(Entity):
    user = models.OneToOneField(User, null=True, blank=True, verbose_name='user', related_name='merchant',
                                on_delete=models.CASCADE)
    name = models.CharField('name', max_length=255)

    class Meta:
        verbose_name = 'merchant'
        verbose_name_plural = 'merchants'

    def __str__(self):
        return self.name


class VendorRating(Entity):
    rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True,
                             blank=True)
    vendor = models.ForeignKey('account.Vendor', on_delete=models.CASCADE, related_name='vendor_rating')
    user = models.ForeignKey(User, related_name='vendor_rating', on_delete=models.CASCADE)

    def __int__(self):
        return self.id


class Order(Entity):
    user = models.ForeignKey(User, verbose_name='user', related_name='orders', null=True, blank=True,
                             on_delete=models.CASCADE)
    address = models.ForeignKey('commerce.Address', verbose_name='address', null=True, blank=True,
                                on_delete=models.CASCADE)
    total = models.DecimalField('total', blank=True, null=True, max_digits=10, decimal_places=2)
    status = models.ForeignKey('commerce.OrderStatus', verbose_name='status', related_name='orders',
                               on_delete=models.CASCADE)
    note = models.CharField('note', null=True, blank=True, max_length=255)
    ref_code = models.CharField('ref code', max_length=255)
    ordered = models.BooleanField('ordered')
    items = models.ManyToManyField('commerce.Item', verbose_name='items', related_name='order')
    promo = models.ForeignKey('commerce.Promo', verbose_name='promo', related_name='orders', null=True, blank=True,
                              on_delete=models.CASCADE)
    shipping = models.DecimalField('shipping', blank=True, null=True, max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'order'
        verbose_name_plural = 'orders'

    def __str__(self):
        return f'{self.user.first_name}'

    @property
    def order_total(self):
        order_total = sum(
            i.product.lowest * i.item_qty for i in self.items.all()
        )

        if self.promo:
            promotype = self.promo.type
            if promotype == 'fixed':
                order_total -= self.promo.amount
            elif promotype == 'percentage':
                order_total -= order_total * self.promo.amount / 100
        return order_total

    @property
    def order_shipment(self):
        promotype = '' if not self.promo else self.promo.type
        if not self.address:
            return 0
        if promotype == 'free_shipping':
            return 0
        destination = self.address.city.name
        map_ = DeliveryMap.objects.get(destination__name=destination)
        return map_.cost


class Item(Entity):
    """
    Product can live alone in the system, while
    Item can only live within an order
    """
    user = models.ForeignKey(User, verbose_name='user', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('commerce.Product', verbose_name='product',
                                on_delete=models.CASCADE)
    item_qty = models.IntegerField('item_qty')
    ordered = models.BooleanField('ordered')

    class Meta:
        verbose_name = 'item'
        verbose_name_plural = 'items'

    def __str__(self):
        return f'{self.product.name}'


class OrderStatus(Entity):
    NEW = 'NEW'  # Order with reference created, items are in the basket.
    PROCESSING = 'PROCESSING'  # Payment confirmed, processing order.
    SHIPPED = 'SHIPPED'  # Shipped to customer.
    COMPLETED = 'COMPLETED'  # Completed and received by customer.
    REFUNDED = 'REFUNDED'  # Fully refunded by seller.

    title = models.CharField('title', max_length=255, choices=[
        (NEW, NEW),
        (PROCESSING, PROCESSING),
        (SHIPPED, SHIPPED),
        (COMPLETED, COMPLETED),
        (REFUNDED, REFUNDED),
    ])
    is_default = models.BooleanField('is default')

    class Meta:
        verbose_name = 'order status'
        verbose_name_plural = 'order status'

    def __str__(self):
        return self.title


class Promo(Entity):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField('name', null=True, blank=True, max_length=255)
    code = models.CharField('code', unique=True, null=True, blank=True, max_length=255)
    description = models.TextField('description', null=True, blank=True)
    is_active = models.BooleanField('is active', null=True, blank=True)
    type = models.CharField('type', choices=(
        ('percentage', 'percentage'),
        ('fixed', 'fixed'),
        ('free_shipping', 'free_shipping'),
    ), null=True, blank=True, max_length=255)
    amount = models.DecimalField('amount', null=True, blank=True, max_digits=10, decimal_places=2)
    active_from = models.DateTimeField('active from', null=True, blank=True)
    active_till = models.DateTimeField('active till', null=True, blank=True)

    class Meta:
        verbose_name = 'promo'
        verbose_name_plural = 'promos'

    def __str__(self):
        return self.name


class PromoUsage(Entity):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    promo = models.ForeignKey(Promo, null=True, blank=True, on_delete=models.SET_NULL)


class Category(MPTTModel, Entity):
    parent = TreeForeignKey('self', verbose_name='parent', related_name='children',
                            null=True,
                            blank=True,
                            on_delete=models.CASCADE)
    name = models.CharField('name', max_length=255)
    description = models.TextField('description')
    image = models.ImageField('image', upload_to='category/')
    is_active = models.BooleanField('is active')
    slug = models.SlugField('slug')

    created = models.DateField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)

    class MPTTMeta:
        order_inspired_by = ['parent']

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.parent:
            return f'-   {self.name}'
        return f'{self.name}'

    @property
    def children(self):
        return self.get_children()


class Label(Entity):
    name = models.CharField('name', max_length=255)

    class Meta:
        verbose_name = 'label'
        verbose_name_plural = 'labels'

    def __str__(self):
        return self.name


class City(Entity):
    name = models.CharField('city', max_length=255)

    class Meta:
        verbose_name = 'city'
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name


class Address(Entity):
    user = models.ForeignKey(User, verbose_name='user', related_name='address',
                             on_delete=models.CASCADE)
    work_address = models.BooleanField('work address', null=True, blank=True)
    address1 = models.CharField('address1', max_length=255)
    address2 = models.CharField('address2', null=True, blank=True, max_length=255)
    city = models.ForeignKey(City, related_name='addresses', on_delete=models.CASCADE)
    phone = models.CharField('phone', max_length=255)

    class Meta:
        verbose_name = 'address'
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f'{self.user.first_name} - {self.address1} - {self.address2} - {self.phone}'


class DeliveryMap(Entity):
    source = models.ForeignKey('commerce.City', verbose_name='source', on_delete=models.CASCADE,
                               related_name='delivery_map_source')
    destination = models.ForeignKey('commerce.City', verbose_name='destination', on_delete=models.CASCADE,
                                    related_name='delivery_map_destination')
    cost = models.DecimalField('cost', max_digits=10, decimal_places=0)

    class Meta:
        verbose_name_plural = 'delivery map'
        verbose_name = 'delivery map'

    def __str__(self):
        return f'{self.source.name} -> {self.destination.name}'
