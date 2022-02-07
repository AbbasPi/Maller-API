from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router, Form, File
from ninja.files import UploadedFile
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import Merchant, Category, Label, ProductImage, Product, ProductRating, VendorRating
from commerce.scehmas import MessageOut, MerchantOut, CategoryOut, LabelOut, ImageOut, ProductRatingOut, \
    ProductRatingCreate, VendorRatingOut, VendorRatingCreate

User = get_user_model()

category_controller = Router(tags=['Categories'])
merchant_controller = Router(tags=['Merchants'])
label_controller = Router(tags=['Labels'])
product_image_controller = Router(tags=['Product images'])
product_rating_controller = Router(tags=['Product rating'])
vendor_rating_controller = Router(tags=['Vendor rating'])


@product_image_controller.get('all', response={
    200: List[ImageOut],
    404: MessageOut
})
def get_product_image(request):
    product_image_qs = ProductImage.objects.all()
    if product_image_qs:
        return 200, product_image_qs
    return 404, {'message': 'image not found'}


@product_image_controller.get('{pk}', response={
    200: List[ImageOut],
    404: MessageOut
})
def get_image_by_product_id(request, pk: UUID4):
    image_qs = ProductImage.objects.filter(product__id=pk)
    if image_qs:
        return 200, image_qs
    return 404, {'message': 'image not found'}


@product_image_controller.post('add', auth=GlobalAuth(), response={
    201: MessageOut,
    400: MessageOut
})
def add_image(request, product_id: UUID4, is_default: bool, image_in: UploadedFile = File(...)):
    product = get_object_or_404(Product, id=product_id, vendor__user_id=request.auth['pk'])
    ProductImage.objects.create(image=image_in, product_id=product.pk, is_default_image=is_default)
    return 201, {'message': 'image added successfully'}


@product_image_controller.put('add', auth=GlobalAuth(), response={
    201: MessageOut,
    400: MessageOut
})
def update_image(request, product_id: UUID4, is_default: bool, image_in: UploadedFile = File(...)):
    product = get_object_or_404(Product, id=product_id, vendor__user_id=request.auth['pk'])
    ProductImage.objects.update(image=image_in, product_id=product.pk, is_default_image=is_default)
    return 201, {'message': 'image updated successfully'}


@label_controller.get('all', response={
    200: List[LabelOut],
    404: MessageOut
})
def get_labels(request):
    label_qs = Label.objects.all()
    if label_qs:
        return 200, label_qs
    return 404, {'message': 'not found'}


@category_controller.get('all', response={
    200: List[CategoryOut],
    404: MessageOut
})
def get_categories(request):
    category_qs = Category.objects.all()
    if category_qs:
        return 200, category_qs
    return 404, {'message': 'no categories found'}


@merchant_controller.get('all', response={
    200: List[MerchantOut],
    404: MessageOut
})
def get_all_merchants(request):
    merchant_qs = Merchant.objects.all()
    if merchant_qs:
        return 200, merchant_qs
    return 404, {'message': 'no merchants found'}


@product_rating_controller.get('{pk}', response={
    200: List[ProductRatingOut],
    404: MessageOut
})
def get_product_rating(request, pk: UUID4):
    product_rating_qs = ProductRating.objects.filter(product__id=pk)
    if product_rating_qs:
        return 200, product_rating_qs
    return 404, {'message': 'no product ratings found'}


@product_rating_controller.post('', auth=GlobalAuth(), response={
    201: MessageOut,
    400: MessageOut
})
def add_product_rating(request, rating_in: ProductRatingCreate):
    rating_data = rating_in.dict()
    if rating_data['rate'] > 5 or rating_data['rate'] < 1:
        return 400, {'message': 'rate must be between 1-5'}
    user = User.objects.get(id=request.auth['pk'])
    try:
        if ProductRating.objects.get(product__id=rating_data['product_id'],
                                     user=user):
            return 400, {'message': 'you can\'t rate the same product twice'}
    except ProductRating.DoesNotExist:
        instance = ProductRating.objects.create(**rating_data)
        instance.user.add(user)
        return 201, {'message': 'product rating added successfully'}


@vendor_rating_controller.get('{pk}', response={
    200: List[VendorRatingOut],
    404: MessageOut
})
def get_vendor_rating(request, pk: UUID4):
    vendor_rating_qs = VendorRating.objects.filter(vendor__id=pk)
    if vendor_rating_qs:
        return 200, vendor_rating_qs
    return 404, {'message': 'no vendor ratings found'}


@vendor_rating_controller.post('', auth=GlobalAuth(), response={
    201: MessageOut,
    400: MessageOut
})
def add_vendor_rating(request, rating_in: VendorRatingCreate):
    vendor_data = rating_in.dict()
    if vendor_data['rate'] > 5 or vendor_data['rate'] < 1:
        return 400, {'message': 'rate must be between 1-5'}
    user = User.objects.get(id=request.auth['pk'])
    try:
        if VendorRating.objects.get(vendor_id=vendor_data['vendor_id'],
                                    user=user):
            return 400, {'message': 'you can\'t rate the same vendor twice'}
    except VendorRating.DoesNotExist:
        instance = VendorRating.objects.create(**vendor_data)
        instance.user.add(user)
        return 201, {'message': 'vendor rating added successfully'}


@vendor_rating_controller.put('{pk}', auth=GlobalAuth(), response={
    200: MessageOut,
    400: MessageOut
})
def edit_vendor_rating(request, pk: UUID4, rating_in: VendorRatingCreate):
    rating_data = rating_in.dict()
    VendorRating.objects.filter(id=pk, user=request.auth['pk']).update(**rating_data)
    return 200, {'message': 'updated successfully'}
