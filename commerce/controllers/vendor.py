from typing import List

from django.contrib.auth import get_user_model
from django.db.models import Q
from ninja import Router, File
from ninja.files import UploadedFile
from pydantic import UUID4

from account.models import Vendor
from account.schemas import VendorOut, VendorEdit
from commerce.models import Product
from commerce.schemas import PaginatedProductDataOut
from config.utils import status
from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut
from config.utils.utils import response

User = get_user_model()

vendor_controller = Router(tags=['Vendors'])


@vendor_controller.get('all', response={
    200: List[VendorOut],
    404: MessageOut
})
def get_vendors(request, q: str = None):
    if not q:
        vendor_qs = Vendor.objects.all()
    if q:
        vendor_qs = Vendor.objects.filter(
            Q(name__icontains=q) | Q(products__name__icontains=q)
        )
    if vendor_qs:
        return 200, vendor_qs
    return 404, {'message': 'no vendors found'}


@vendor_controller.get('{pk}', response={
    200: VendorOut,
    404: MessageOut
})
def retrieve_vendor(request, pk: UUID4):
    vendor_qs = Vendor.objects.get(id=pk)
    if vendor_qs:
        return 200, vendor_qs
    return 404, {'message': 'vendor not found'}


@vendor_controller.get('', auth=AuthBearer(), response={
    200: VendorOut,
    404: MessageOut
})
def get_vendor(request):
    vendor_qs = Vendor.objects.get(user=request.auth)
    if vendor_qs:
        return 200, vendor_qs
    return 404, {'message': 'vendor not found'}


@vendor_controller.post('', auth=AuthBearer(), response={
    200: MessageOut,
    400: MessageOut
})
def edit_vendor_image(request, image_in: UploadedFile = File(...)):
    Vendor.objects.filter(user=request.auth).update(image=image_in.name)
    return 200, {'message': 'image edited successfully'}


@vendor_controller.put('', auth=AuthBearer(), response={
    200: MessageOut
})
def edit_vendor(request, vendor_in: VendorEdit):
    vendor_data = vendor_in.dict()
    Vendor.objects.filter(user=request.auth).update(**vendor_data, user=request.auth)
    return 200, {'message': 'updated successfully'}


@vendor_controller.get('vendor/products', auth=AuthBearer(), response={200: PaginatedProductDataOut})
def get_vendor_products(request, per_page: int = 12, page: int = 1):
    """
    Get the products of the vendor that's currently logged in
    """
    product_qs = Product.objects.filter(vendor__user=request.auth)
    if not product_qs:
        return response(status.HTTP_404_NOT_FOUND, {"message": "No vendor products found"})

    return response(status.HTTP_200_OK, product_qs, paginated=True, per_page=per_page, page=page)


@vendor_controller.get('vendor/products/{pk}', response={200: PaginatedProductDataOut})
def get_vendor_products_by_id(request, pk:UUID4, per_page: int = 12, page: int = 1):
    product_qs = Product.objects.filter(vendor__id=pk)
    if not product_qs:
        return response(status.HTTP_404_NOT_FOUND, {"message": "No vendor products found"})

    return response(status.HTTP_200_OK, product_qs, paginated=True, per_page=per_page, page=page)
