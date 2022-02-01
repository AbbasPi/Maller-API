from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import City
from commerce.scehmas import CityOut, MessageOut, CityCreate

User = get_user_model()


city_controller = Router(tags=['Cities'])


@city_controller.get('all', response={
    200: List[CityOut],
    404: MessageOut
})
def get_all_cities(request):
    cities_qs = City.objects.all()
    if cities_qs:
        return 200, cities_qs
    return 404, {'detail': 'No cities found'}


@city_controller.get('{pk}', response={
    200: CityOut,
    404: MessageOut
})
def get_city_by_id(request, pk: UUID4):
    cities_qs = City.objects.get(id=pk)
    if cities_qs:
        return 200, cities_qs
    return 404, {'detail': 'No cities found'}


@city_controller.delete('{pk}', auth=GlobalAuth(), response={
    202: MessageOut
})
def delete_city(request, pk: UUID4):
    city = get_object_or_404(City, id=pk)
    city.delete()
    return 202, {'message': 'city deleted'}


@city_controller.get('', auth=GlobalAuth(), response={
    200: CityOut,
    404: MessageOut
})
def get_user_city(request):
    cities_qs = City.objects.get(addresses__user=request.auth['pk'])
    if cities_qs:
        return 200, cities_qs
    return 404, {'detail': 'No cities found'}


@city_controller.post('', auth=GlobalAuth(), response={
    201: CityOut,
    400: MessageOut
})
def create_city(request, city_in: CityCreate):
    city_data = city_in.dict()
    city = City.objects.create(**city_data)
    return 201, city


@city_controller.put('update/{pk}', auth=GlobalAuth(), response={
    200: CityOut,
    400: MessageOut
})
def update_city(request, pk: UUID4, city_in: CityCreate):
    city_data = city_in.dict()
    City.objects.filter(id=pk).update(**city_data)
    city_qs = City.objects.get(id=pk)
    if city_qs:
        return 200, city_qs
    return 400, {'message': 'something went wrong'}

