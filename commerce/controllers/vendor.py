from typing import List

from django.contrib.auth import get_user_model
from django.db.models import Q
from ninja import Router, File
from ninja.files import UploadedFile
from pydantic import UUID4

from account.authorization import GlobalAuth
from account.models import Vendor
from account.schemas import VendorOut, VendorEdit
from commerce.scehmas import MessageOut

User = get_user_model()

vendor_controller = Router(tags=['Vendors'])


@vendor_controller.get('all', response={
    200: List[VendorOut],
    404: MessageOut
})
def get_vendors(request, q: str = None):
    if not q:
        vendor_qs = Vendor.objects.all()
    elif q:
        vendor_qs = Vendor.objects.filter(
            Q(store_name__icontains=q) | Q(description__icontains=q) | Q(products__name__icontains=q)
        )
    if vendor_qs:
        return 200, vendor_qs
    return 404, {'message': 'no vendors found'}


@vendor_controller.get('{pk}', auth=GlobalAuth(), response={
    200: VendorOut,
    404: MessageOut
})
def get_vendor_by_id(request, pk: UUID4):
    vendor_qs = Vendor.objects.get(id=pk)
    if vendor_qs:
        return 200, vendor_qs
    return 404, {'message': 'vendor not found'}


@vendor_controller.get('', auth=GlobalAuth(), response={
    200: VendorOut,
    404: MessageOut
})
def get_vendor(request):
    user_pk = User.objects.get(id=request.auth['pk'])
    vendor_qs = Vendor.objects.get(user=user_pk)
    if vendor_qs:
        return 200, vendor_qs
    return 404, {'message': 'vendor not found'}


@vendor_controller.put('', auth=GlobalAuth(), response={
    200: MessageOut
})
def edit_vendor(request, vendor_in: VendorEdit):
    user_pk = User.objects.get(id=request.auth['pk'])
    vendor_data = vendor_in.dict()
    Vendor.objects.filter(user=user_pk).update(**vendor_data, user=user_pk)
    return 200, {'message': 'updated successfully'}


@vendor_controller.put('edit', auth=GlobalAuth(), response={
    201: MessageOut,
    400: MessageOut
})
def edit_vendor_image(request, image_in: UploadedFile = File(...)):
    Vendor.objects.filter(user_id=request.auth['pk']).update(image=image_in)
    return 201, {'message': 'image edited successfully'}
