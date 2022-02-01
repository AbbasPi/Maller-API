from typing import List
from ninja import ModelSchema, Schema
from pydantic import UUID4, Field

from account.schemas import VendorOut, AccountOut
from commerce.models import Product, ProductRating, VendorRating, ProductImage, Merchant, Order, \
    Address, City, Label, Category


class UUIDSchema(Schema):
    id: UUID4


class MessageOut(Schema):
    message: str


class CategoryOut(UUIDSchema):
    name: str
    description: str
    image: str
    children: List['CategoryOut'] = None


CategoryOut.update_forward_refs()


class MerchantOut(UUIDSchema):
    name: str


class LabelOut(UUIDSchema):
    name: str


class ProductOut(ModelSchema):
    vendor: VendorOut
    label: LabelOut
    merchant: MerchantOut
    category: CategoryOut

    class Config:
        model = Product
        model_fields = ['id',
                        'name',
                        'description',
                        'qty',
                        'price',
                        'discounted_price',
                        'vendor',
                        'category',
                        'label',
                        'merchant',
                        'height',
                        'width',
                        'weight',
                        'length'
                        ]


class ProductCreate(Schema):
    name: str
    description: str = None
    qty: int
    price: int
    discounted_price: int = None
    cost: int
    height: int = None
    width: int = None
    weight: int = None
    length: int = None
    is_active: bool
    is_featured: bool
    category_id: UUID4
    label_id: UUID4
    merchant_id: UUID4


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
    city_id: UUID4
    address1: str
    address2: str
    work_address: bool
    phone: int


class ProductRatingOut(UUIDSchema):
    rate: int


class ProductRatingCreate(Schema):
    rate: int


class VendorRatingOut(UUIDSchema):
    rate: int


class VendorRatingCreate(Schema):
    rate: int


class ItemSchema(Schema):
    user: AccountOut
    product: ProductOut
    item_qty: int
    ordered: bool


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int


class ItemOut(UUIDSchema, ItemSchema):
    pass


class ImageOut(UUIDSchema):
    user: UUID4
    product: str
    item_qty: int
    ordered: bool


class ImageCreate(ImageOut):
    pass
