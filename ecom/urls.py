from django.contrib import admin
from django.urls import path

from .views import (
    CheckoutView,
    PaymentView,
    add_to_cart,
    HomeListView, 
    ItemDetailView, 
    OrderSummaryView,
    remove_from_cart,
    remove_single_item_from_cart
)

urlpatterns = [
    path('', HomeListView.as_view(), name='landing-page'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment')
]