from typing import List

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from account.authorization import GlobalAuth
from account.models import Vendor
from commerce.models import Product
from commerce.scehmas import ProductOut, MessageOut, ProductCreate

User = get_user_model()

product_controller = Router(tags=['Products'])


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

    return 200, products_qs


@product_controller.get('/{pk}', response={
    200: List[ProductOut],
    404: MessageOut

})
def get_product_by_id(request, pk: UUID4):
    product_qs = get_object_or_404(Product, id=pk)
    if product_qs:
        return 200, product_qs
    return 404, {'message': 'product not found'}


@product_controller.get('', auth=GlobalAuth(), response=List[ProductOut])
def get_vendor_products(request):
    """
    Get the products of the vendor that's currently logged in
    """
    product_qs = Product.objects.filter(vendor__user__id=request.auth['pk'])
    if product_qs:
        return 200, product_qs
    return 404, {'message': 'product not found'}


@product_controller.post('', auth=GlobalAuth(), response={
    201: MessageOut,
    400: MessageOut,
})
def create_vendor_products(request, product_in: ProductCreate):
    product_data = product_in.dict()
    user_pk = User.objects.get(id=request.auth['pk'])
    vendor_instance = get_object_or_404(Vendor, user=user_pk)
    product_data.pop('merchant_id')
    product_data.pop('label_id')
    product_data.pop('category_id')
    Product.objects.create(**product_data, vendor=vendor_instance,
                           category_id=product_in.category_id, label_id=product_in.label_id,
                           merchant_id=product_in.merchant_id
                           )

    return 201, {'message': 'product created successfully'}


@product_controller.put('update/{pk}', auth=GlobalAuth(), response={
    200: ProductOut,
    400: MessageOut,
})
def update_vendor_products(request, pk: UUID4, product_in: ProductCreate):
    vendor_instance = get_object_or_404(Vendor, user__id=request.auth['pk'])
    product_data = product_in.dict()
    product_data.pop('merchant_id')
    product_data.pop('label_id')
    product_data.pop('category_id')
    Product.objects.filter(pk=pk).update(**product_data, vendor=vendor_instance,
                                         category_id=product_in.category_id, label_id=product_in.label_id,
                                         merchant_id=product_in.merchant_id)
    product_qs = Product.objects.get(pk=pk)
    return 200, product_qs


@product_controller.delete('delete/{pk}', auth=GlobalAuth(), response={
    202: MessageOut
})
def delete_vendor_products(request, pk: UUID4):
    product = get_object_or_404(Product, id=pk, vendor__user__id=request.auth['pk'])
    product.delete()

    return 202, {'message': 'product deleted successfully'}
