from typing import List
from ninja import ModelSchema, Schema
from pydantic import UUID4
from ninja.orm import create_schema

from account.models import Vendor
from config.utils.schemas import Paginated, UUIDSchema
from account.schemas import AccountOut
from commerce.models import Address, OrderStatus, Promo


class CategoryDataOut(Schema):
    pk: UUID4
    name: str
    description: str
    image: str
    slug: str
    children: List['CategoryDataOut'] = None


CategoryDataOut.update_forward_refs()

PromoDataOut = create_schema(Promo, exclude=['created', 'updated', 'active_from', 'active_till'])

VendorDataOut = create_schema(Vendor, exclude=['created', 'updated'])


class MerchantOut(UUIDSchema):
    name: str


class ProductRatingOut(UUIDSchema):
    rate: int


class ProductRatingCreate(Schema):
    rate: int
    product_id: UUID4


class VendorRatingOut(UUIDSchema):
    rate: int


class VendorRatingCreate(Schema):
    rate: int
    vendor_id: UUID4


class LabelOut(UUIDSchema):
    name: str


class ImageCreate(Schema):
    product_id: UUID4
    is_default_image: bool
    alt_text: str = None


class ProductImageDataOut(UUIDSchema, ImageCreate):
    image: str
    pass


class ImageEdit(Schema):
    is_default_image: bool
    alt_text: str


class ProductDataOut(UUIDSchema):
    name: str
    average_rating: int
    slug: str
    description: str
    in_stock: bool
    qty: int
    lowest: float
    lowest_discounted: float = None
    weight: float = None
    width: int = None
    height: float = None
    length: float = None
    vendor: VendorDataOut
    category: CategoryDataOut = None
    merchant: MerchantOut = None
    is_featured: bool
    is_active: bool
    label: LabelOut = None
    images: List[ProductImageDataOut]
    product_rating: List[ProductRatingOut]


class PaginatedProductDataOut(Schema):
    total_count: int
    per_page: int
    from_record: int
    to_record: int
    previous_page: int
    current_page: int
    next_page: int
    page_count: int
    data: List[ProductDataOut]


class PaginatedProductManyOut(Paginated):
    data: List[ProductDataOut]


class ProductCreate(Schema):
    name: str
    description: str = None
    lowest: int
    lowest_discounted: int = None
    qty: int
    height: int = None
    width: int = None
    weight: int = None
    length: int = None
    is_active: bool
    is_featured: bool
    category_id: UUID4
    label_id: UUID4
    merchant_id: UUID4
    is_default_image: bool


class CityOut(UUIDSchema):
    name: str


class CityCreate(Schema):
    name: str


class AddressOut(ModelSchema):
    user: AccountOut
    city: CityOut

    class Config:
        model = Address
        model_fields = [
            'id',
            'work_address',
            'address1',
            'address2',
            'phone'
        ]


class AddressCreate(Schema):
    address1: str
    address2: str
    work_address: bool
    city_id: UUID4
    phone: int


class ItemDataOut(UUIDSchema):
    product: ProductDataOut
    item_qty: int
    ordered: bool


class ItemIn(Schema):
    product_id: UUID4
    item_qty: int = None


OrderStatusDataOut = create_schema(OrderStatus, exclude=['id', 'created', 'updated'])


class OrderDataOut(Schema):
    pk: UUID4
    user: AccountOut
    address: AddressOut = None
    order_total: float
    status: OrderStatusDataOut
    note: str = None
    ref_code: str
    ordered: bool
    items: List[ItemDataOut]
    promo: PromoDataOut = None
    order_shipment: float = None


class OrderIn(Schema):
    items: List[UUID4]


class NoteUpdateDataIn(Schema):
    note: str


class PromoDataIn(Schema):
    promo_code: str
    order_id: UUID4
