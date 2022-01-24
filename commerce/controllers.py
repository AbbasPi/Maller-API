from ninja import Router
from typing import List

from account.models import Vendor, User, Customer

from commerce.models import Product, Merchant
from commerce.scehmas import ProductOut

product_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])


@product_controller.get('', response=List[ProductOut])
def get_products(request):
    return Product.objects.all()



