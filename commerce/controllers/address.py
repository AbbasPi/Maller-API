from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import Address, User, City
from commerce.scehmas import AddressOut, MessageOut, AddressCreate

User = get_user_model()

address_controller = Router(tags=['Addresses'])


@address_controller.get('all', response={
    200: List[AddressOut],
    404: MessageOut
})
def get_addresses(request):
    address_qs = Address.objects.all()
    if address_qs:
        return 200, address_qs
    return 404, {'message': 'No addresses found'}


@address_controller.get('user', auth=GlobalAuth(), response={
    200: AddressOut,
    404: MessageOut
})
def get_user_address(request):
    user_pk = User.objects.get(id=request.auth['pk'])
    address_qs = Address.objects.get(user_id=user_pk)
    if address_qs:
        return 200, address_qs
    return 404, {'message': 'address not found'}


@address_controller.get('{pk}', response={
    200: AddressOut,
    404: MessageOut
})
def get_address_by_id(request, pk: UUID4):
    address_qs = Address.objects.get(id=pk)
    if address_qs:
        return 200, address_qs
    return 404, {'message': 'No address found'}


@address_controller.post('', auth=GlobalAuth(), response={
    200: AddressOut,
    400: MessageOut
})
def create_address(request, address_in: AddressCreate):
    address_data = address_in.dict()
    city_pk = address_data.pop('city_id')
    city_instance = get_object_or_404(City, pk=city_pk)
    user_pk = User.objects.get(id=request.auth['pk'])
    address_qs = Address.objects.create(**address_data, user=user_pk, city=city_instance)
    if address_qs:
        return 200, address_qs
    return 400, {'message': 'something went wrong'}


@address_controller.put('{pk}', auth=GlobalAuth(), response={
    200: AddressOut,
    400: MessageOut
})
def update_address(request, pk: UUID4, address_in: AddressCreate):
    address_data = address_in.dict()
    city_pk = address_data.pop('city_id')
    city_instance = get_object_or_404(City, pk=city_pk)
    user_pk = User.objects.get(id=request.auth['pk'])
    Address.objects.filter(user=user_pk, pk=pk).update(**address_data, city=city_instance, user=user_pk)
    address_qs = Address.objects.get(pk=pk)
    if address_qs:
        return 200, address_qs
    return 400, {'something went wrong'}


@address_controller.delete('{pk}', auth=GlobalAuth(), response={
    202: MessageOut
})
def delete_address(request, pk: UUID4):
    address = get_object_or_404(Address, pk=pk, user=request.auth['pk'])
    address.delete()
    return 202, {'message': 'address deleted'}

