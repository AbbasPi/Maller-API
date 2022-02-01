import http
from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from account.authorization import GlobalAuth
from commerce.models import Item
from commerce.scehmas import ItemOut, MessageOut, ItemCreate

User = get_user_model()

cart_controller = Router(tags=['Carts'])


@cart_controller.get('my', auth=GlobalAuth(), response={
    200: List[ItemOut],
    404: MessageOut
})
def view_cart(request):
    cart_items = Item.objects.filter(user=request.auth['pk'], ordered=False)
    if cart_items:
        return 200, cart_items
    return 404, {'message': 'no items in the cart'}


@cart_controller.post('my', auth=GlobalAuth(), response={
    200: MessageOut,
    400: MessageOut
})
def add_to_cart(request, item_in: ItemCreate):
    try:
        item = Item.objects.get(product_id=item_in.product_id, user_id=request.auth['pk'], ordered=False)
        if item_in.item_qty < 1:
            return 400, {'message': 'Quantity Value Must be Greater Than Zero'}
        if item_in.item_qty > 0:
            item.item_qty += item_in.item_qty
        item.save()
    except Item.DoesNotExist:
        if item_in.item_qty < 1:
            return 400, {'message': 'Quantity Value Must be Greater Than Zero'}
        Item.objects.create(**item_in.dict(), user_id=request.auth['pk'])
    return 200, {'message': 'added to cart successfully'}


@cart_controller.post('item/reduce/{pk}', auth=GlobalAuth(), response={
    200: MessageOut,
    401: MessageOut
})
def reduce_item_quantity(request, pk: UUID4):
    item = get_object_or_404(Item, id=pk, user_id=request.auth['pk'], ordered=False)
    if item.item_qty <= 1:
        item.delete()
        return {'message': 'item deleted'}
    item.item_qty -= 1
    item.save()
    return {'message': 'item quantity reduced'}


@cart_controller.post('item/increase/{pk}', auth=GlobalAuth(), response={
    200: MessageOut,
    401: MessageOut
})
def increase_item_quantity(request, pk: UUID4):
    item = get_object_or_404(Item, id=pk, user_id=request.auth['pk'], ordered=False)
    item.item_qty += 1
    item.save()
    return {'message': 'item quantity increased'}


@cart_controller.delete('item/delete/{pk}', auth=GlobalAuth(), response={
    202: MessageOut,
    401: MessageOut
})
def delete_item(request, pk: UUID4):
    item = get_object_or_404(Item, id=pk, user_id=request.auth['pk'])
    item.delete()
    return 202, {'message': 'item deleted successfully'}
