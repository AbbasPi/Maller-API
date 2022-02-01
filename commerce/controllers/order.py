import random
import string
from typing import List

from django.contrib.auth import get_user_model
from ninja import Router

from account.authorization import GlobalAuth
from commerce.models import Order, OrderStatus, Item
from commerce.scehmas import MessageOut

User = get_user_model()

order_controller = Router(tags=['Orders'])


def gen_ref_code(length=4):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


@order_controller.post('', auth=GlobalAuth(), response={
    200: MessageOut,
    404: MessageOut,
    401: MessageOut
})
def create_order(request):
    user = User.objects.prefetch_related('items', 'orders').get(id=request.auth['pk'])
    user_items = user.items.filter(ordered=False)
    if not user_items:
        return 404, {'detail': 'No Items Found To added to Order'}

    try:

        order = user.orders.prefetch_related('items').get(ordered=False)
        list_of_productID_in_order = [item['product_id'] for item in order.items.values('product_id')]
        list_of_difference_items = []
        list_of_intersection_items = [
            (item, item.item_qty) if item.product_id in list_of_productID_in_order else list_of_difference_items.append(
                item.id) for item in user_items]
        Item.objects.filter(id__in=list_of_difference_items).update(ordered=True)

        for item, qty in list(filter(None, list_of_intersection_items)):
            item_duplicated = order.items.get(product_id=item.product_id)
            item_duplicated.item_qty = item_duplicated.item_qty + qty
            item_duplicated.save()
            item.delete()

        order.items.add(*list_of_difference_items)
        order.total = order.order_total
        order.save()
        return 200, {'detail': 'order updated successfully!'}
    except Order.DoesNotExist:
        order_status, _ = OrderStatus.objects.get_or_create(title='NEW', is_default=True)
        order = Order.objects.create(user=user, status=order_status, ref_code=gen_ref_code(6), ordered=False)
        order.items.set(user_items)
        order.total = order.order_total
        user_items.update(ordered=True)
        order.save()
        return 200, {'detail': 'Order Created Successfully!'}
