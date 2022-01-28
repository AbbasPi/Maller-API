from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from typing import List
from django.contrib.auth import get_user_model
from pydantic import UUID4

from account.models import Vendor
from commerce.models import Product, Address, ProductRating, Merchant, Label, Category
from commerce.scehmas import ProductOut, MessageOut, ProductRatingOut, AddressOut, ProductIn
from account.authorization import GlobalAuth

User = get_user_model()

product_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])
category_controller = Router(tags=['categories'])


# Product Endpoints

@product_controller.get('all', response={
    200: List[ProductOut],
    404: MessageOut
})
def list_products(request, *, price_from: int = None, price_to: int = None, vendor: UUID4 = None,
                  category: UUID4 = None, merchant: UUID4 = None, label: UUID4 = None, search: str = None
                  ):
    products_qs = Product.objects.filter(is_active=True).select_related('merchant', 'vendor', 'category', 'label')

    if not products_qs:
        return 404, {'detail': 'No products found'}

    if price_from:
        products_qs = products_qs.filter(discounted_price__gte=price_from)

    if price_to:
        products_qs = products_qs.filter(discounted_price__lte=price_to)

    if vendor:
        products_qs = products_qs.filter(vendor__id=vendor)

    if merchant:
        products_qs = products_qs.filter(merchant__id=merchant)

    if label:
        products_qs = products_qs.filter(label__id=label)

    if category:
        products_qs = products_qs.filter(category__id=category)

    if search:
        products_qs = products_qs.filter(
            Q(name__icontains=search) | Q(description__icontains=search) | Q(category__name__icontains=search)
            | Q(merchant__name__icontains=search) | Q(vendor__store_name__icontains=search)
            | Q(category__description__icontains=search) | Q(vendor__description__icontains=search)
        )

    return products_qs


@product_controller.get('/{pk}', response=List[ProductOut])
def get_product_by_id(request, pk: UUID4):
    return Product.objects.filter(id=pk)


@product_controller.get('', auth=GlobalAuth(), response=List[ProductOut])
def get_vendor_products(request):
    """
    Get the products of the vendor that's currently logged in
    """
    return Product.objects.filter(vendor__user__id=request.auth['pk'])


@product_controller.post('product/', auth=GlobalAuth(), response={
    201: ProductOut,
    400: MessageOut,
})
def create_vendor_products(request, product_in: ProductIn):
    product_data = product_in.dict()
    vendor_instance = get_object_or_404(Vendor, user__id=request.auth['pk'])
    product_data.pop('merchant_id')
    product_data.pop('label_id')
    product_data.pop('category_id')
    product_qs = Product.objects.create(**product_data, vendor=vendor_instance,
                                        category_id=product_in.category_id, label_id=product_in.label_id,
                                        merchant_id=product_in.merchant_id
                                        )

    return 201, product_qs


@product_controller.put('product/{pk}', auth=GlobalAuth(), response={
    200: ProductOut,
    400: MessageOut,
})
def update_vendor_products(request, pk: UUID4, product_in: ProductIn):
    vendor_instance = get_object_or_404(Vendor, user__id=request.auth['pk'])
    product_data = product_in.dict()
    product_data.pop('merchant_id')
    product_data.pop('label_id')
    product_data.pop('category_id')
    product_pk = Product.objects.filter(pk=pk).update(**product_data, vendor=vendor_instance,
                                                      category_id=product_in.category_id, label_id=product_in.label_id,
                                                      merchant_id=product_in.merchant_id)
    product_qs = Product.objects.get(pk=pk)
    return 200, product_qs


@product_controller.delete('product/{pk}', auth=GlobalAuth(), response={
    204: MessageOut
})
def delete_vendor_products(request, pk: UUID4):
    product = get_object_or_404(Product, id=pk, vendor__user__id=request.auth['pk'])
    product.delete()

    return 204, {'message': ''}
