import time, re, json, requests, base64, os
from datetime import datetime

from flask import (
    current_app,
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_babel import lazy_gettext
from flask_login import current_user, login_required
from flask_mail import Mail, Message
from pluggy import HookimplMarker

from flaskshop.account.models import User, UserAddress
from flaskshop.product.models import ProductVariant, Product, AttributeChoiceValue
from flaskshop.constant import OrderStatusKinds, PaymentStatusKinds, ShipStatusKinds, get_state_abbrev, get_color
from flaskshop.extensions import csrf_protect
# from .payment import zhifubao
import stripe
from .models import Order, OrderPayment, OrderLine


stripe.api_key = os.getenv('stripe_api_key')


impl = HookimplMarker("flaskshop")


@login_required
def index():
    return redirect(url_for("account.index"))


@login_required
def show(token):
    order = Order.query.filter_by(token=token).first()
    if order is None:
        abort(403, lazy_gettext("This is not your order!"))
    if not order.is_self_order:
        abort(403, lazy_gettext("This is not your order!"))
    return render_template("orders/details.html", order=order)


def create_payment(token, payment_method):
    # print(printiful_order)
    order = Order.query.filter_by(token=token).first()
    if order.status != OrderStatusKinds.unfulfilled.value:
        abort(403, lazy_gettext("This Order Can Not Be Completed"))
    payment_no = str(int(time.time())) + str(current_user.id)
    customer_ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    payment = OrderPayment.query.filter_by(order_id=order.id).first()
    if payment:
        payment.update(
            payment_method=payment_method,
            payment_no=payment_no,
            customer_ip_address=customer_ip_address,
        )
    else:
        payment = OrderPayment.create(
            order_id=order.id,
            payment_method=payment_method,
            payment_no=payment_no,
            status=PaymentStatusKinds.waiting.value,
            total=order.total,
            customer_ip_address=customer_ip_address,
        )
    if payment_method == "alipay":
        redirect_url = zhifubao.send_order(order.token, payment_no, order.total)
        payment.redirect_url = redirect_url
    return payment


# def printiful_order(request):




# @login_required
# def ali_pay(token):
#     payment = create_payment(token, "alipay")
#     return redirect(payment.redirect_url)
#
#
# @csrf_protect.exempt
# def ali_notify():
#     data = request.form.to_dict()
#     success = zhifubao.verify_order(data)
#     if success:
#         order_payment = OrderPayment.query.filter_by(
#             payment_no=data["out_trade_no"]
#         ).first()
#         order_payment.pay_success(paid_at=data["gmt_payment"])
#         return "SUCCESS"
#     return "ERROR HAPPEND"



# def create_checkout_session(token):
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
#                     'price': 'price_1N4VYWJs9hh3tFE1lbS7ppli',
#                     'quantity': 1,
#                 },
#             ],
#             mode='payment',
#             success_url= 'http://127.0.0.1' + '/orders/payment_success.html',
#             cancel_url= 'http://127.0.0.1' + '/orders/details.html',
#             automatic_tax={'enabled': True},
#         )
#     except Exception as e:
#         return str(e)
#
#     return redirect(checkout_session.url, code=303)


@login_required
def test_pay_flow(token):
    payment = create_payment(token, "stripe_pay")
    order = Order.query.filter_by(token=token).first()
    payment = OrderPayment.query.filter_by(order_id=order.id).first()
    stripe_pmt = OrderLine.query.filter_by(order_id=order.id).first()
    line_id_is = re.sub('\D', '', str(stripe_pmt))
    strip_price = OrderLine.query.get(line_id_is)
    order_user_id = order.user_id
    user_email_address = User.query.get(order_user_id)
    user_address = UserAddress.query.get(order_user_id)
    line_items = OrderLine.query.filter_by(order_id=order.id)
    line_items_list = []
    for line_item in line_items:
        create_strp_price = stripe.Price.create(
                                    unit_amount = int(float(line_item.unit_price_net)*100),
                                    currency = "usd",
                                    product = line_item.product_id)
        create_strp_qnty = line_item.quantity
        itm_dict = {}
        itm_dict['price'] = create_strp_price
        itm_dict['quantity'] = create_strp_qnty
        line_items_list.append(itm_dict)
    try:
        # stripe.Customer.create(
        #     id = user_email_address.email,
        #     description= user_address.contact_name,
        #     )
        checkout_session = stripe.checkout.Session.create(
            # shipping_address_collection={"allowed_countries": ["US"]},
            customer=current_user.id,
            shipping_options=[
            {
                "shipping_rate_data": {
                "type": "fixed_amount",
                "fixed_amount": {"amount": int(float(order.shipping_price_net)*100), "currency": "usd"},
                "display_name": order.shipping_method_name,
                "delivery_estimate": {
                    "minimum": {"unit": "business_day", "value": 5},
                    "maximum": {"unit": "business_day", "value": 7},
                },
                },
            },
            ],
            line_items=line_items_list,
            # shipping_address_collection = {'enabled': True},
            # customer_email = user_email_address.email,
            mode = 'payment',
            success_url = 'https://glenbertsfish.com' + '/orders/payment_success/' + str(token),
            cancel_url = 'https://glenbertsfish.com' + '/orders/' + str(token),
            automatic_tax = {'enabled': True},
            # billing_address_collection = {'enabled': True},
            )
    except Exception as e:
        return str(e)
    # return redirect(url_for("order.payment_success"))
    return redirect(checkout_session.url, code=303)



pnt_token = os.getenv('pnt_token')
url_base = "https://api.printful.com/"
get_products_url = "https://api.printful.com/sync/products"
# url = 'https://www.printful.com/oauth/'
headers = {'Authorization': 'Bearer ' + str(pnt_token),
            'Content-Type': 'application/json'}

@login_required
def payment_success(token):
    payment = create_payment(token, "stripe_pay")
    order = Order.query.filter_by(token=token).first()
    order_num = str(order.token)
    email_order_num = order_num.rsplit('-', 3)
    order_user_id = order.user_id
    user_email_address = User.query.get(order_user_id)
    msg = Message(subject = 'Hello, Order#' + str(email_order_num[3]) + ' is processing!' ,
                sender = ('Glenberts Fish Co.', 'orders@glenbertsfish.com'),
                recipients = [user_email_address.email],
                reply_to = None
                )
    msg.html = render_template("orders/order_email.html", order=order)
    mail = Mail(current_app)
    mail.send(msg)
    payment.pay_success(paid_at=datetime.now())
    line_items = OrderLine.query.filter_by(order_id=order.id)
    get_usr_address = UserAddress.query.filter_by(user_id=order_user_id).first()
    cust = stripe.Customer.retrieve(str(current_user.id))
    stripe_cust_address=cust['address']
    stripe_cust_name=cust['shipping']
    print(stripe_cust_address['city'])
    order_json = {
        "recipient": {
            "name": stripe_cust_name['name'],
            "address1": stripe_cust_address['line1'],
            "city": stripe_cust_address['city'],
            "state_name": stripe_cust_address['state'],
            "state_code": get_state_abbrev(stripe_cust_address['state']),
            "country_code": 'US',
            "zip": stripe_cust_address['postal_code']
        },
        "items": [{}],
        "retail_costs": {
            "currency": "USD",
            "subtotal":  int(float(order.total_net)),
            "discount":  int(float(order.discount_amount)),
            "shipping":  int(float(order.shipping_price_net)),
            },
    }
    # order_json['retail_costs'] = { "shipping": int(float(order.shipping_price_net)*100) }
    items = []
    for line_item in line_items:
        cat_code = Product.get_by_id(line_item.product.id)
        # print(cat_code.attributes)
        if '13' in cat_code.attributes:
            embro_color = AttributeChoiceValue.query.filter_by(id=cat_code.attributes['13']).first()
            color = get_color(embro_color.title)
        else:
            color = None
        if cat_code.product_type_id == 8:
            get_file_id = ProductVariant.get_by_id(line_item.variant.id)
            item = {
                "variant_id": line_item.product_sku.split('-')[1],
                "quantity": line_item.quantity,
                "retail_price": int(float(line_item.unit_price_net)),
                "files": [{
                        "id": line_item.stripe_price_id,
                            }],
                "options" : [{
                          "id" : "thread_colors",
                          "value" : [color]
                       },
                    ],
            }
            items.append(item)
        if cat_code.product_type_id == 1:
            get_file_id = ProductVariant.get_by_id(line_item.variant.id)
            item = {
                # "variant_id": line_item.product_sku.split('-')[1],
                "quantity": line_item.quantity,
                "retail_price": int(float(line_item.unit_price_net)),
                "external_variant_id": line_item.product_sku.split('-')[1],
                # "files": [{
                #         "id": line_item.stripe_price_id,
                #             }],
                # "options" : [{
                #           "id" : "thread_colors",
                #           "value" : [color]
                #        },
                #     ],
            }
            items.append(item)    
            
    order_json['items'] = items
    url = 'https://api.printful.com/orders'
    headers = {'Authorization': 'Bearer ' + pnt_token,
                'Content-Type': 'application/json'}
    try:
        # get_resp = requests.get(get_products_url, headers=headers)
        # print(get_resp)
        # print(json.dumps(printful_request.json(),indent=4))
        response = requests.post(url, data=json.dumps(order_json),
                                 headers=headers)
        # response = requests.post(url, data=jimport,
        #                          headers=headers)
        # print("get_resp = ", get_resp.status_code, get_resp.text)
        # print("response = ", response.status_code, response.text)
        # return True, response
    except requests.exceptions.RequestException as e:
        print("ERROR: When submitting order with requests, "
              "error message: %s" % str(e))
        return False, e
    return render_template("orders/checkout_success.html", order=order)


@login_required
def cancel_order(token):
    order = Order.query.filter_by(token=token).first()
    if not order.is_self_order:
        abort(403, "This is not your order!")
    order.cancel()
    return render_template("orders/details.html", order=order)


@login_required
def receive(token):
    order = Order.query.filter_by(token=token).first()
    order.update(
        status=OrderStatusKinds.completed.value,
        ship_status=ShipStatusKinds.received.value,
    )
    return render_template("orders/details.html", order=order)


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("order", __name__)
    bp.add_url_rule("/", view_func=index)
    bp.add_url_rule("/<string:token>", view_func=show)
    # bp.add_url_rule("/pay/<string:token>/alipay", view_func=ali_pay)
    # bp.add_url_rule("/alipay/notify", view_func=ali_notify, methods=["POST", "HEAD"])
    bp.add_url_rule("/pay/<string:token>/testpay", view_func=test_pay_flow)
    bp.add_url_rule("/payment_success/<string:token>", view_func=payment_success)
    bp.add_url_rule("/cancel/<string:token>", view_func=cancel_order)
    bp.add_url_rule("/receive/<string:token>", view_func=receive)
    app.register_blueprint(bp, url_prefix="/orders")
