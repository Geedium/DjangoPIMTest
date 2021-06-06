from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView, DetailView, View
from .models import BillingAddress, Item, Order, OrderItem
from .forms import CheckoutForm

# Create your views here.
def item_list(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request,"products.djt", context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        # form
        form = CheckoutForm()

        context = {
            'form': form
        }

        return render(self.request, "checkout.djt", context)

    def post(self, *args, **kwargs):
        # form
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user =self.request.user, ordered=False)

            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address, 
                    apartment_address = apartment_address,
                    country = country,
                    zip = zip
                )

                billing_address.save()
                
                order.billing_address = billing_address
                order.save()

                return redirect('checkout')

            messages.warning(self.request, "Failed checkout")
            return redirect('checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order-summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.djt')

class HomeListView(ListView):
    model = Item
    paginate_by = 10
    template_name='products.djt'

class ItemDetailView(DetailView):
    model = Item
    template_name='product.djt'

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user = self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.djt', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have active order.")
            return redirect("/")

        return render(self.request, 'order_summary.djt')

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            # item exists in cart increase quantity
            order_item.quantity += 1
            order_item.save()

            messages.info(request, "This item quantity was updated.")
            return redirect('order-summary')
        else:
            messages.info(request, "This item was added to your cart.")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        messages.info(request, "This item was added to your cart.")
        order.items.add(order_item)

    return redirect('product', slug=slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    # Check if order is not ordered yet.
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists(): # It is already ordered.
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            # retrieve order
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect('order-summary')
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('product', slug=slug)
    else:
        messages.info(request, "You do not have active order.")
        return redirect('product', slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    # Check if order is not ordered yet.
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists(): # It is already ordered.
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            # retrieve order
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "This item quantity was updated.")
            return redirect('order-summary')
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('product', slug=slug)
    else:
        messages.info(request, "You do not have active order.")
        return redirect('product', slug=slug)