"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from account.controllers import account_controller
from commerce.controllers.address import address_controller
from commerce.controllers.cart import cart_controller
from commerce.controllers.city import city_controller
from commerce.controllers.order import order_controller
from commerce.controllers.others import category_controller, merchant_controller, product_image_controller, \
    label_controller
from commerce.controllers.product import product_controller
from commerce.controllers.vendor import vendor_controller


from config import settings

maller = NinjaAPI()

maller.add_router('auth', account_controller)
maller.add_router('vendor', vendor_controller)
maller.add_router('product', product_controller)
maller.add_router('product-image', product_image_controller)
maller.add_router('cart', cart_controller)
maller.add_router('order', order_controller)
maller.add_router('address', address_controller)
maller.add_router('city', city_controller)
maller.add_router('category', category_controller)
maller.add_router('label', label_controller)
maller.add_router('merchant', merchant_controller)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('maller/', maller.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)