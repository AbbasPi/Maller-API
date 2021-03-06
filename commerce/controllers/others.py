from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router, File
from ninja.files import UploadedFile
from pydantic import UUID4

from commerce.schemas import ImageEdit, ImageCreate
from commerce.models import Merchant, Category, Label, ProductImage, Product, ProductRating, VendorRating
from commerce.schemas import MerchantOut, LabelOut, ProductRatingOut, ProductRatingCreate, VendorRatingOut, \
    VendorRatingCreate, CategoryDataOut, PaginatedProductDataOut
from config.utils import status
from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut
from config.utils.utils import response

User = get_user_model()

category_controller = Router(tags=['Categories'])
merchant_controller = Router(tags=['Merchants'])
label_controller = Router(tags=['Labels'])
product_image_controller = Router(tags=['Product images'])
product_rating_controller = Router(tags=['Product rating'])
vendor_rating_controller = Router(tags=['Vendor rating'])


@product_image_controller.post('edit/{pk}', auth=AuthBearer(), response={
    201: MessageOut,
    400: MessageOut
})
def update_image(request, pk: UUID4, image: ImageEdit, image_in: UploadedFile = File(...)):
    get_object_or_404(Product, images__id=pk, vendor__user_id=request.auth)
    image_data = image.dict()
    ProductImage.objects.filter(id=pk).update(image=f'product/{image_in}', **image_data)
    return 201, {'message': 'image updated successfully'}


@product_image_controller.post('', auth=AuthBearer(), response={
    201: MessageOut,
    400: MessageOut
})
def add_image(request, image: ImageCreate, image_in: UploadedFile = File(...)):
    image_data = image.dict()
    product_instance = image_data.pop('product_id')
    product = get_object_or_404(Product, id=product_instance, vendor__user_id=request.auth)
    ProductImage.objects.create(image=f'product/{image_in}', **image_data, product_id=product_instance)
    return 201, {'message': 'image added successfully'}


@product_image_controller.delete('{pk}', auth=AuthBearer(), response={
    202: MessageOut
})
def delete_image(request, pk: UUID4):
    image_qs = get_object_or_404(ProductImage, id=pk)
    image_qs.delete()
    return 202, {'message': 'image deleted successfully'}


@label_controller.get('all', response={
    200: List[LabelOut],
    404: MessageOut
})
def get_labels(request):
    label_qs = Label.objects.all()
    if label_qs:
        return 200, label_qs
    return 404, {'message': 'not found'}


@label_controller.get('{pk}', response={
    200: PaginatedProductDataOut,
    404: MessageOut
})
def get_label_product(request, pk: UUID4, per_page: int = 12, page: int = 1):
    if pk is None:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'no label specified'})
    try:
        label = Label.objects.get(pk=pk)
    except Label.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'label does not exist'})
    products = (
        Product.objects.filter(label__id=pk).select_related('label', 'category', 'vendor', 'merchant')
    )

    return response(status.HTTP_200_OK, products, paginated=True, per_page=per_page, page=page)


@category_controller.get('all', response={
    200: List[CategoryDataOut],
    404: MessageOut
})
def get_categories(request):
    category_qs = Category.objects.filter(is_active=True).filter(parent=None)
    if category_qs:
        return 200, category_qs
    return 404, {'message': 'no categories found'}


@category_controller.get('{pk}', response={
    200: List[CategoryDataOut],
    404: MessageOut
})
def retrieve_category(request, pk: UUID4):
    category_qs = Category.objects.filter(is_active=True, id=pk).filter(parent=None)
    if category_qs:
        return 200, category_qs
    return 404, {'message': 'no categories found'}


@category_controller.get('{pk}/products', response={
    200: PaginatedProductDataOut,
    404: MessageOut
})
def category_products(request, pk: UUID4, per_page: int = 12, page: int = 1):
    if pk is None:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'No category specified'})
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'Category does not exist'})
    products = (
        Product.objects.filter(category__in=category.get_descendants(include_self=True))
            .select_related('category', 'vendor', 'merchant')
    )

    return response(status.HTTP_200_OK, products, paginated=True, per_page=per_page, page=page)


@merchant_controller.get('all', response={
    200: List[MerchantOut],
    404: MessageOut
})
def get_all_merchants(request):
    merchant_qs = Merchant.objects.all()
    if merchant_qs:
        return 200, merchant_qs
    return 404, {'message': 'no merchants found'}


@merchant_controller.get('{pk}/products', response={
    200: PaginatedProductDataOut,
    404: MessageOut
})
def merchant_products(request, pk: UUID4, per_page: int = 12, page: int = 1):
    if pk is None:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'no merchant specified'})
    try:
        merchant = Merchant.objects.get(pk=pk)
    except Merchant.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'merchant does not exist'})
    products = (
        Product.objects.filter(merchant__id=pk)
            .select_related('category', 'vendor', 'merchant')
    )

    return response(status.HTTP_200_OK, products, paginated=True, per_page=per_page, page=page)


@product_rating_controller.get('{pk}', response={
    200: List[ProductRatingOut],
    404: MessageOut
})
def get_product_rating(request, pk: UUID4):
    product_rating_qs = ProductRating.objects.filter(product__id=pk)
    if product_rating_qs:
        return 200, product_rating_qs
    return 404, {'message': 'no product ratings found'}


@product_rating_controller.post('', auth=AuthBearer(), response={
    201: MessageOut,
    400: MessageOut
})
def add_product_rating(request, rating_in: ProductRatingCreate):
    rating_data = rating_in.dict()
    if rating_data['rate'] > 5 or rating_data['rate'] < 1:
        return 400, {'message': 'rate must be between 1-5'}
    user = request.auth
    try:
        if ProductRating.objects.get(product__id=rating_data['product_id'],
                                     user=user):
            ProductRating.objects.filter(product__id=rating_data['product_id'],
                                         user=user).update(**rating_data)
            return 201, {'message': f'product rating updated'}
    except ProductRating.DoesNotExist:
        instance = ProductRating.objects.create(**rating_data, user=user)
        return 201, {'message': 'product rating added successfully'}


@product_rating_controller.delete('{pk}', auth=AuthBearer(), response={
    203: MessageOut
})
def delete_product_rating(request, pk: UUID4):
    product_rating_qs = ProductRating.objects.get(user=request.auth, product__id=pk)
    product_rating_qs.delete()
    return 203, {'message': 'deleted successfully'}


@vendor_rating_controller.get('{pk}', response={
    200: List[VendorRatingOut],
    404: MessageOut
})
def get_vendor_rating(request, pk: UUID4):
    vendor_rating_qs = VendorRating.objects.filter(vendor__id=pk)
    if vendor_rating_qs:
        return 200, vendor_rating_qs
    return 404, {'message': 'no vendor ratings found'}


@vendor_rating_controller.post('', auth=AuthBearer(), response={
    201: MessageOut,
    400: MessageOut
})
def add_vendor_rating(request, rating_in: VendorRatingCreate):
    vendor_data = rating_in.dict()
    if vendor_data['rate'] > 5 or vendor_data['rate'] < 1:
        return 400, {'message': 'rate must be between 1-5'}
    try:
        if VendorRating.objects.get(vendor_id=vendor_data['vendor_id'],
                                    user=request.auth):
            VendorRating.objects.filter(vendor_id=vendor_data['vendor_id'],
                                        user=request.auth).update(**vendor_data)
            return 201, {'message': 'rating updated'}
    except VendorRating.DoesNotExist:
        VendorRating.objects.create(**vendor_data, user=request.auth)
        return 201, {'message': 'vendor rating added successfully'}


@vendor_rating_controller.delete('{pk}', auth=AuthBearer(), response={
    203: MessageOut
})
def delete_vendor_rating(request, pk: UUID4):
    vendor_rating_qs = get_object_or_404(VendorRating, id=pk, user=request.auth)
    if vendor_rating_qs:
        vendor_rating_qs.delete()
    return 203, {'message': 'deleted successfully'}
