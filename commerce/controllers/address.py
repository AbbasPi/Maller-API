from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from config.utils.permissions import AuthBearer
from commerce.models import Address, City
from commerce.schemas import AddressOut, AddressCreate, CityOut
from config.utils.schemas import MessageOut

address_controller = Router(tags=['Addresses'])


@address_controller.get('', response={
    200: List[AddressOut],
    404: MessageOut
})
def get_addresses(request):
    address_qs = Address.objects.all()
    if address_qs:
        return 200, address_qs
    return 404, {'message': 'No addresses found'}


@address_controller.get('address', auth=AuthBearer(), response={
    200: List[AddressOut],
    404: MessageOut
})
def get_user_address(request):
    address_qs = Address.objects.filter(user=request.auth)
    if address_qs:
        return 200, address_qs
    return 404, {'message': 'address not found'}


@address_controller.get('{pk}', auth=AuthBearer(), response={
    200: List[AddressOut],
    404: MessageOut
})
def retrieve_address(request, pk: UUID4):
    address_qs = Address.objects.filter(id=pk, user=request.auth).select_related('city')
    if address_qs:
        return 200, address_qs
    return 404, {'message': 'No address found'}


@address_controller.post('', auth=AuthBearer(), response={
    200: AddressOut,
    400: MessageOut
})
def create_address(request, address_in: AddressCreate):
    address_data = address_in.dict()
    city_pk = address_data.pop('city_id')
    city_instance = get_object_or_404(City, pk=city_pk)
    address_qs = Address.objects.create(**address_data, user=request.auth, city=city_instance)
    if address_qs:
        return 200, address_qs
    return 400, {'message': 'something went wrong'}


@address_controller.put('{pk}', auth=AuthBearer(), response={
    200: MessageOut,
    400: MessageOut
})
def update_address(request, pk: UUID4, address_in: AddressCreate):
    address_data = address_in.dict()
    city_pk = address_data.pop('city_id')
    city_instance = get_object_or_404(City, pk=city_pk)
    Address.objects.filter(user=request.auth, pk=pk).update(**address_data, city=city_instance)
    address_qs = Address.objects.get(pk=pk)
    if address_qs:
        return 200, {'message': 'address created successfully' }
    return 400, {'message': 'something went wrong'}


@address_controller.delete('{pk}', auth=AuthBearer(), response={
    202: MessageOut
})
def delete_address(request, pk: UUID4):
    address = get_object_or_404(Address, pk=pk, user=request.auth)
    address.delete()
    return 202, {'message': 'address deleted'}


@address_controller.get('city/all', response={
    200: List[CityOut],
    404: MessageOut
})
def get_all_cities(request):
    cities_qs = City.objects.all()
    if cities_qs:
        return 200, cities_qs
    return 404, {'detail': 'No cities found'}


@address_controller.get('city/{pk}', response={
    200: CityOut,
    404: MessageOut
})
def retrieve_city(request, pk: UUID4):
    cities_qs = City.objects.get(id=pk)
    if cities_qs:
        return 200, cities_qs
    return 404, {'detail': 'No cities found'}
