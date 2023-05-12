import time, re, json
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

from flaskshop.account.models import User
from flaskshop.constant import OrderStatusKinds, PaymentStatusKinds, ShipStatusKinds
from flaskshop.extensions import csrf_protect
# from .payment import zhifubao
import stripe
from .models import Order, OrderPayment, OrderLine


stripe.api_key = 'sk_test_51N4QgvJs9hh3tFE1WZuvEtRkdsrvJzZnh4hlJMDE08snk478wGBuMpHvLFZlKtxK53XvAlP23YJqHl5F2wnjeYed0097p4sGbR'


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
        # stripe.ShippingRate.create(
        #             display_name="Ground shipping",
        #             type="fixed_amount",
        #             fixed_amount={"amount": 500, "currency": "usd"})
        checkout_session = stripe.checkout.Session.create(
            shipping_address_collection={"allowed_countries": ["US"]},
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
            #     {
            #
            #
            #         # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
            #         # 'price': 'price_1N4VYWJs9hh3tFE1lbS7ppli',
            #         # 'price': strip_price.stripe_price_id,
            #         # 'quantity': strip_price.quantity,
            #
            #         'price': stripe.Price.create(
            #                                     unit_amount = int(float(order.total_net)*100),
            #                                     currency = "usd",
            #                                     product = "1"),
            #         'quantity': strip_price.quantity,
            #         # 'shipping_options.shipping_rate': stripe.ShippingRate.create(
            #         #             display_name="Ground shipping",
            #         #             type="fixed_amount",
            #         #             fixed_amount={"amount": 500, "currency": "usd"})
            #
            #     },
            # ],
            customer_email = user_email_address.email,
            mode = 'payment',
            success_url = 'https://glenbertsfish.com' + '/orders/payment_success/' + str(token),
            cancel_url = 'https://glenbertsfish.com' + '/orders/' + str(token),
            automatic_tax = {'enabled': True},
            )

            # if checkout_session.payment_status != 'unpaid':
            #     print(checkout_session)
            #     payment.pay_success(paid_at=datetime.now())
    except Exception as e:
        return str(e)
    # if success_url is not None:
    #     payment.pay_success(paid_at=datetime.now())
    # payment.pay_success(paid_at=datetime.now())
    # return redirect(url_for("order.payment_success"))
    return redirect(checkout_session.url, code=303)




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
    # payment_no = request.args.get("success_url")
    payment.pay_success(paid_at=datetime.now())
    # if payment:
    #     res = zhifubao.query_order(payment)
    #     if res["code"] == "303":
    #         order_payment = OrderPayment.query.filter_by(
    #             payment=res["out_trade_no"]
    #         ).first()
    #         order_payment.pay_success(paid_at=res["send_pay_date"])
    #     else:
    #         print(res["msg"])

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
