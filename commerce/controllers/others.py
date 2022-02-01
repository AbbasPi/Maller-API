from typing import List

from django.contrib.auth import get_user_model
from ninja import Router

from commerce.models import Merchant, Category, Label, ProductImage
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


# @product_image_controller.post('add', auth=GlobalAuth(), response={
#     201: ImageOut,
#     400: MessageOut
# })
# def add_image(request, product_id: UUID4, is_default: bool, image_in: UploadedFile = Form(...)):
#     # vendor_instance = get_object_or_404(Vendor, user__id=request.auth['pk'])
#     product = get_object_or_404(Product, id=image_in.product_id, vendor__user_id=request.auth['pk'])
#     image_qs = ProductImage.objects.create(image=image_in, product_id=product.pk, is_default_image=is_default)
#     return 201, image_qs


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


