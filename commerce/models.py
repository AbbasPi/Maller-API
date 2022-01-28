import uuid
from PIL import Image
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth import get_user_model
from account.models import Vendor

User = get_user_model()


class Entity(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)


class Product(Entity):
    name = models.CharField('name', max_length=255)
    description = models.CharField('description', max_length=1000, null=True, blank=True)
    weight = models.FloatField('weight', null=True, blank=True)
    width = models.FloatField('width', null=True, blank=True)
    height = models.FloatField('height', null=True, blank=True)
    length = models.FloatField('length', null=True, blank=True)
    qty = models.DecimalField('qty', max_digits=10, decimal_places=2)
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    cost = models.DecimalField('cost', max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField('discounted price', max_digits=10, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField('is featured')
    is_active = models.BooleanField('is active')
    vendor = models.ForeignKey('account.Vendor', verbose_name='vendor', related_name='products',
                               on_delete=models.SET_NULL,
                               null=True, blank=True)
    category = models.ForeignKey('commerce.Category', verbose_name='category', related_name='products',
                                 blank=True, null=True, on_delete=models.CASCADE)
    merchant = models.ForeignKey('commerce.Merchant', verbose_name='merchant', related_name='products',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    label = models.ForeignKey('commerce.Label', verbose_name='label', related_name='products', null=True, blank=True,
                              on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ProductRating(Entity):
    rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True,
                             blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_rating')
    user = models.ManyToManyField(User, related_name='product_rating')

    def __int__(self):
        return self.product.name


class VendorRating(Entity):
    rate = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], null=True,
                             blank=True)
    vendor = models.ForeignKey('account.Vendor', on_delete=models.CASCADE, related_name='vendor_rating')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_rating')

    def __int__(self):
        return self.rate


class Order(Entity):
    user = models.ForeignKey(User, verbose_name='user', related_name='orders', null=True, blank=True,
                             on_delete=models.CASCADE)
    address = models.ForeignKey('commerce.Address', verbose_name='address', null=True, blank=True,
                                on_delete=models.CASCADE)
    status = models.ForeignKey('commerce.OrderStatus', verbose_name='status', related_name='orders',
                               on_delete=models.CASCADE)
    note = models.CharField('note', null=True, blank=True, max_length=255)
    ref_code = models.CharField('ref code', max_length=255)
    ordered = models.BooleanField('ordered')
    items = models.ManyToManyField('commerce.Item', verbose_name='items', related_name='order')

    def __str__(self):
        return f'{self.user.first_name} + {self.order_total}'

    @property
    def order_total(self):
        return sum(
            i.product.discounted_price * i.item_qty for i in self.items.all()
        )


class Item(Entity):
    """
    Product can live alone in the system, while
    Item can only live within an order
    """
    user = models.ForeignKey(User, verbose_name='user', related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('commerce.Product', verbose_name='product',
                                on_delete=models.CASCADE)
    item_qty = models.IntegerField('item_qty')
    ordered = models.BooleanField('ordered', default=False)

    def __str__(self):
        return f''


class OrderStatus(Entity):
    NEW = 'NEW'  # Order with reference created, items are in the basket.
    # CREATED = 'CREATED'  # Created with items and pending payment.
    # FAILED = 'FAILED'  # Payment failed, retry is available.
    # CANCELLED = 'CANCELLED'  # Cancelled by seller, stock increased.
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

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Order Status'
        verbose_name_plural = 'Order Statuses'


class Category(Entity):
    parent = models.ForeignKey('self',
                               verbose_name='parent',
                               related_name='children',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    name = models.CharField('name', max_length=255)
    description = models.TextField('description')
    image = models.ImageField('image', upload_to='category/')
    is_active = models.BooleanField('is active')

    def __str__(self):
        if self.parent:
            return f'-   {self.name}'
        return f'{self.name}'

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    @property
    def children(self):
        return self.children


class ProductImage(Entity):
    image = models.ImageField('image', upload_to='product/')
    is_default_image = models.BooleanField('is default image')
    product = models.ForeignKey('commerce.Product', verbose_name='product', related_name='images',
                                on_delete=models.CASCADE)

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


class Label(Entity):
    name = models.CharField('name', max_length=255)

    class Meta:
        verbose_name = 'label'
        verbose_name_plural = 'labels'

    def __str__(self):
        return self.name


class Merchant(Entity):
    name = models.CharField('name', max_length=255)

    def __str__(self):
        return f'{self.name} - {self.id}'


class City(Entity):
    name = models.CharField('city', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'city'
        verbose_name_plural = 'cities'


class Address(Entity):
    user = models.ForeignKey(User, verbose_name='user', related_name='address',
                             on_delete=models.CASCADE)
    work_address = models.BooleanField('work address', null=True, blank=True)
    address1 = models.CharField('address1', max_length=255)
    address2 = models.CharField('address2', null=True, blank=True, max_length=255)
    city = models.ForeignKey(City, related_name='addresses', on_delete=models.CASCADE)
    phone = models.CharField('phone', max_length=255)

    def __str__(self):
        return f'{self.user.first_name} - {self.address1} - {self.address2} - {self.phone}'

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
