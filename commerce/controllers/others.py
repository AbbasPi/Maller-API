from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router, Form, File
from ninja.files import UploadedFile
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import Merchant, Category, Label, ProductImage, Product
from commerce.scehmas import MessageOut, MerchantOut, CategoryOut, LabelOut, ImageOut

User = get_user_model()

category_controller = Router(tags=['Categories'])
merchant_controller = Router(tags=['Merchants'])
label_controller = Router(tags=['Labels'])
product_image_controller = Router(tags=['Product images'])


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
