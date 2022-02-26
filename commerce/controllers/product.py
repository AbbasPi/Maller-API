from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.files import UploadedFile
from pydantic import UUID4

from account.models import Vendor
from commerce.models import Product, ProductImage
from commerce.schemas import ProductCreate, PaginatedProductDataOut, ProductDataOut
from config.utils import status
from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut
from config.utils.utils import response

User = get_user_model()

product_controller = Router(tags=['Products'])


@product_controller.get('/all', auth=None, response={
    200: PaginatedProductDataOut,
    404: MessageOut
})
def all_products(request, lowest_gte=None, lowest_lte=None, category_name=None,
                 merchant_name=None, vendor_id: UUID4 = None, is_featured=None, label_name=None,
                 search=None, per_page: int = 12, page: int = 1,
                 ):
    products_qs = Product.objects.filter(is_active=True).select_related('category', 'vendor', 'merchant')
    if lowest_gte:
        products_qs = products_qs.filter(lowest__gte=lowest_gte)
    if lowest_lte:
        products_qs = products_qs.filter(lowest__lte=lowest_lte)
    if category_name:
        products_qs = products_qs.filter(category__name=category_name)
    if merchant_name:
        products_qs = products_qs.filter(merchant__name=merchant_name)
    if vendor_id:
        products_qs = products_qs.filter(vendor=vendor_id)
    if is_featured:
        products_qs = products_qs.filter(is_featured=is_featured)
    if label_name:
        products_qs = products_qs.filter(label__name=label_name)

    if search:
        products_qs = products_qs.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    if products_qs:
        return response(status.HTTP_200_OK, products_qs, paginated=True, per_page=per_page, page=page)
    return 404, {'message': 'product not found'}


@product_controller.get('/{pk}', response={
    200: ProductDataOut,
    404: MessageOut

})
def retrieve_product(request, pk: UUID4):
    product_qs = get_object_or_404(Product, id=pk)
    if product_qs:
        return 200, product_qs
    return 404, {'message': 'product not found'}


@product_controller.post('', auth=AuthBearer(), response={
    201: MessageOut,
    400: MessageOut,
})
def create_vendor_products(request, product_in: ProductCreate, image_in: UploadedFile = File(...)):
    product_data = product_in.dict()
    vendor_instance = get_object_or_404(Vendor, user=request.auth)
    merchant_instance = product_data.pop('merchant_id')
    label_instance = product_data.pop('label_id')
    category_instance = product_data.pop('category_id')
    is_default = product_data.pop('is_default_image')
    product = Product.objects.create(**product_data, vendor=vendor_instance,
                                     category_id=category_instance, label_id=label_instance,
                                     merchant_id=merchant_instance
                                     )
    ProductImage.objects.create(image=f'product/{image_in}', product=product, is_default_image=is_default,
                                alt_text=product.name)
    return 201, {'message': 'product created successfully'}


@product_controller.put('update/{pk}', auth=AuthBearer(), response={
    200: ProductDataOut,
    400: MessageOut,
})
def update_vendor_products(request, pk: UUID4, product_in: ProductCreate):
    vendor_instance = get_object_or_404(Vendor, user=request.auth)
    product_data = product_in.dict()
    product_data.pop('merchant_id')
    product_data.pop('label_id')
    product_data.pop('category_id')
    Product.objects.filter(pk=pk).update(**product_data, vendor=vendor_instance,
                                         category_id=product_in.category_id, label_id=product_in.label_id,
                                         merchant_id=product_in.merchant_id)
    product_qs = Product.objects.get(pk=pk)
    return 200, product_qs


@product_controller.delete('delete/{pk}', auth=AuthBearer(), response={
    202: MessageOut
})
def delete_vendor_products(request, pk: UUID4):
    product = get_object_or_404(Product, id=pk, vendor__user=request.auth)
    product.delete()

    return 202, {'message': 'product deleted successfully'}
