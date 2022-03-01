import random
import string
from typing import List

from django.contrib.auth import get_user_model
from django.utils import timezone
from ninja import Router
from pydantic import UUID4

from commerce.models import Order, OrderStatus, Item, PromoUsage, Address, Promo
from commerce.schemas import OrderDataOut, OrderIn, NoteUpdateDataIn, PromoDataIn
from config.utils import status
from config.utils.permissions import AuthBearer
from config.utils.schemas import MessageOut
from config.utils.utils import response

User = get_user_model()

order_controller = Router(tags=['Orders'])


def time_active_promo(promo):
    seconds_from = (timezone.now() - promo.active_from).total_seconds()
    # print(seconds_from)
    seconds_to = (timezone.now() - promo.active_till).total_seconds()
    # print(seconds_to)
    return seconds_from > 1 and seconds_to < 1


def usage_active_promo(user, promo):
    usage = PromoUsage.objects.filter(user=user).filter(promo=promo)
    return not usage.exists()


def create_ref_code() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def gen_ref_code(length=4):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


@order_controller.get('', auth=AuthBearer(), response={
    200: List[OrderDataOut],
    404: MessageOut
})
def all_orders(request, ordered: bool = False):
    order_qs = Order.objects.order_by('pk').filter(user=request.auth)
    if not ordered:
        order_qs = order_qs.filter(ordered=ordered)
    if not order_qs:
        return 404, {'message': 'no active orders'}
    return 200, order_qs


@order_controller.post('', auth=AuthBearer(), response={
    200: MessageOut,
    401: MessageOut
})
def create_update(request, items_in: OrderIn):
    items = Item.objects.filter(id__in=items_in.items)

    existing_order = Order.objects.filter(user=request.auth, ordered=False)

    if existing_order.exists():
        order_ = existing_order.first()
        for i in items:
            i.ordered = True
            i.save()
        order_.items.add(*items)
        order_.save()
        return response(status.HTTP_200_OK, {"message": "order updated successfully"})
    else:
        for i in items:
            i.ordered = True
            i.save()
        default_status = OrderStatus.objects.get(title="NEW")
        order_ = Order.objects.create(
            user=request.auth,
            status=default_status,
            ordered=False,
            ref_code=create_ref_code(),
        )
        order_.items.add(*items)
        order_.save()
        return response(status.HTTP_200_OK, {"message": "order created successfully"})


@order_controller.post('/checkout', auth=AuthBearer(), response={
    200: MessageOut,
    404: MessageOut,
    400: MessageOut
})
def checkout(request):
    try:
        checkout_order = Order.objects.get(ordered=False, user=request.auth)
    except Order.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'Order not found'})
    address = Address.objects.get(user=request.auth)
    checkout_order.address = address
    if not checkout_order.address:
        return response(status.HTTP_400_BAD_REQUEST, {'message': 'order should have an address assigned'})

    checkout_order.shipping = checkout_order.order_shipment
    checkout_order.total = checkout_order.order_total
    for i in checkout_order.items.all():
        if i.product.qty < i.item_qty:
            return response(status.HTTP_404_NOT_FOUND, {
                'message': f'item {i.product.name} is out of stock!'
            })
        i.product.qty -= i.item_qty
        i.product.save()
    checkout_order.ordered = True
    checkout_order.save()
    return response(status.HTTP_200_OK, {'message': 'checkout successful'})


@order_controller.post('/{pk}/update_address', auth=AuthBearer(), response={200: MessageOut, 404: MessageOut})
def update_address(request, order_pk: UUID4, address_pk: UUID4):
    try:
        address = Address.objects.get(pk=address_pk, user=request.auth)
    except Address.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'Address does not exist'})

    try:
        order_qs = Order.objects.get(pk=order_pk, user=request.auth)
    except Order.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'Order does not exist'})

    order_qs.address = address
    order_qs.save()

    return response(status.HTTP_200_OK, {'message': 'address updated successfully'})


@order_controller.post('/{pk}/update_note', auth=AuthBearer(), response={
    200: MessageOut,
    404: MessageOut
})
def update_note(request, pk: UUID4, data_in: NoteUpdateDataIn):
    try:
        order_qs = Order.objects.get(pk=pk, user=request.auth)
    except Order.DoesNotExist:
        return response(status.HTTP_200_OK, {'message': 'Order does not exist'})

    order_qs.note = data_in.note
    order_qs.save()

    return response(status.HTTP_200_OK, {'message': 'order updated successfully'})


@order_controller.post('/promo', auth=AuthBearer(), response={200: MessageOut, 400: MessageOut})
def add_promo(request, data_in: PromoDataIn):
    try:
        promo = Promo.objects.get(code=data_in.promo_code)
    except Promo.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'Address does not exist'})

    try:
        order_qs = Order.objects.get(pk=data_in.order_id, user=request.auth)
    except Order.DoesNotExist:
        return response(status.HTTP_404_NOT_FOUND, {'message': 'Order does not exist'})

    if not promo.is_active:
        return 400, {'message': 'promo code is not valid'}
    elif time_active_promo(promo) and usage_active_promo(request.auth, promo):
        if promo.user:
            if str(promo.user) != str(request.auth):
                return response(status.HTTP_400_BAD_REQUEST,
                                {'message': 'Promo code is not valid or not allowed for you'})

            order_qs.promo = promo
            order_qs.save()
            PromoUsage.objects.create(promo=promo, user=request.auth)
            return response(status.HTTP_200_OK, {'message': 'Promo applied successfully'})
        else:
            order_qs.promo = promo
            order_qs.save()
            PromoUsage.objects.create(promo=promo, user=request.auth)
            return response(status.HTTP_200_OK, {'message': 'promo code added successfully'})
    else:
        return response(status.HTTP_200_OK, {'message': 'promo code is not valid or used'})

