from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Payment, OrderProduct
import json
from store.models import Product
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

import smtplib
from email.message import EmailMessage as RawEmailMessage

def send_email(subject, body, to_email):
    from django.conf import settings
    # Configuration
    smtp_server = settings.EMAIL_HOST
    smtp_port = settings.EMAIL_PORT
    sender_email = settings.EMAIL_HOST_USER
    sender_password = settings.EMAIL_HOST_PASSWORD

    msg = RawEmailMessage()
    msg.set_content(body)
    msg.add_alternative(body, subtype='html')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@require_POST
@login_required(login_url='login')
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, order_number=body['orderID'])

    # 1. Store transaction details (We always save the attempt)
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'], # This could be 'COMPLETED' or something else
    )
    payment.save()

    # CHANGE STARTS HERE: Wrap everything in a success check
    if body['status'] == 'COMPLETED':
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variations.set(product_variation)
            orderproduct.save()

            # Reduce the quantity of the sold products
            product = Product.objects.get(id=item.product_id)
            product.stock -= item.quantity
            product.save()

        # 2. Clear cart ONLY on success
        CartItem.objects.filter(user=request.user).delete()

        # 3. Send email ONLY on success
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = sum(i.product_price * i.quantity for i in ordered_products)
        message = render_to_string('orders/email_template.html', {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        })
        mail_subject = 'Thank you for your order!'
        to_email = request.user.email
        # send email and persist the result in the user's session so the
        # order completion page can show whether the email was sent.
        result = send_email(mail_subject, message, to_email)
        try:
            # store under a key unique to this order number
            request.session[f'email_sent_{order.order_number}'] = bool(result)
        except Exception:
            # don't fail the whole flow if session storage fails
            pass
        
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,            
        }
        return JsonResponse(data)
    
    else:
        # CHANGE: If status is NOT 'COMPLETED', return an error response
        # This prevents the JS .then() from running and keeps the cart full
        return JsonResponse({'status': 'Failed', 'message': 'Payment was not successful'}, status=400)
    
@login_required(login_url='login')
def place_order(request, total=0, quantity=0,):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    print(order_number)
    print(transID)
    try:
        payment = Payment.objects.get(payment_id=transID)
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        
        # Read the email send result from session (set by payments()).
        # Map boolean -> friendly message; if missing, leave as None.
        email_result = request.session.pop(f'email_sent_{order_number}', None)
        if email_result is True:
            email_result = "Email sent successfully"
        elif email_result is False:
            email_result = "Failed to send email"
        else:
            email_result = None

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'email_result': email_result,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

def blank_page(request):
    # Get data from the URL parameters
    order_number = request.GET.get('order_number')
    amount = request.GET.get('amount')
    
    context = {
        'order_number': order_number,
        'amount': amount,
    }

    return render(request, 'orders/blank_page.html', context)

def email_template(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        payment = Payment.objects.get(payment_id=transID)
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        
        html_string = render_to_string('orders/email_template.html', context)
        
        return HttpResponse(html_string)

    except Exception as e:
        return HttpResponse(str(e), status=400)
    
