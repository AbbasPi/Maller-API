from typing import List

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import Item
from commerce.schemas import ItemDataOut, ItemIn
from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut

User = get_user_model()

cart_controller = Router(tags=['Carts'])


@cart_controller.get('my', auth=AuthBearer(), response={
    200: List[ItemDataOut],
    404: MessageOut
})
def view_cart(request):
    cart_items = Item.objects.filter(user=request.auth, ordered=False)
    if cart_items:
        return 200, cart_items
    return 404, {'message': 'no items in the cart'}


@cart_controller.post('my', auth=AuthBearer(), response={
    200: MessageOut,
    400: MessageOut
})
def add_to_cart(request, item_in: ItemIn):
    try:
        item = Item.objects.get(product_id=item_in.product_id, user_id=request.auth, ordered=False)
        if item_in.item_qty < 1:
            return 400, {'message': 'Quantity Value Must be Greater Than Zero'}
        if item_in.item_qty > 0:
            item.item_qty += item_in.item_qty
        item.save()
    except Item.DoesNotExist:
        if item_in.item_qty < 1:
            return 400, {'message': 'Quantity Value Must be Greater Than Zero'}
        Item.objects.create(**item_in.dict(), user=request.auth, ordered=False)
    return 200, {'message': 'added to cart successfully'}


@cart_controller.post('item/reduce/{pk}', auth=AuthBearer(), response={
    200: MessageOut,
    401: MessageOut
})
def reduce_item_quantity(request, pk: UUID4):
    item = get_object_or_404(Item, id=pk, user_id=request.auth, ordered=False)
    if item.item_qty <= 1:
        item.delete()
        return {'message': 'item deleted'}
    item.item_qty -= 1
    item.save()
    return {'message': 'item quantity reduced'}


@cart_controller.post('item/increase/{pk}', auth=AuthBearer(), response={
    200: MessageOut,
    401: MessageOut
})
def increase_item_quantity(request, pk: UUID4):
    item = get_object_or_404(Item, id=pk, user_id=request.auth, ordered=False)
    item.item_qty += 1
    item.save()
    return {'message': 'item quantity increased'}


@cart_controller.delete('item/delete/{pk}', auth=AuthBearer(), response={
    202: MessageOut,
    401: MessageOut
})
def delete_item(request, pk: UUID4):
    item = get_object_or_404(Item, id=pk, user_id=request.auth)
    item.delete()
    return 202, {'message': 'item deleted successfully'}
