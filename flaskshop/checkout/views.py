from flask import abort, Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_babel import lazy_gettext
from flask_login import current_user, login_required
from pluggy import HookimplMarker

from flaskshop.account.forms import AddressForm
from flaskshop.account.models import UserAddress
from flaskshop.discount.models import Voucher
from flaskshop.order.models import Order
from flaskshop.utils import flash_errors
from flaskshop.constant import get_state_abbrev, get_color

import stripe, os

from .forms import NoteForm, VoucherForm
from .models import Cart, CartLine, ShippingMethod
import easypost


client = easypost.EasyPostClient(os.getenv("EASYPOST_API_KEY"))

impl = HookimplMarker("flaskshop")


def cart_index():
    return render_template("checkout/cart.html")


def update_cartline(id):
    # TODO when not enough stock, response ajax error
    line = CartLine.get_by_id(id)
    response = {
        "variantId": line.variant_id,
        "subtotal": 0,
        "total": 0,
        "cart": {"numItems": 0, "numLines": 0},
    }
    if request.form["quantity"] == "0":
        line.delete()
    else:
        line.quantity = int(request.form["quantity"])
        line.save()
    cart = Cart.query.filter(Cart.user_id == current_user.id).first()
    response["cart"]["numItems"] = cart.update_quantity()
    response["cart"]["numLines"] = len(cart)
    response["subtotal"] = "$" + str(line.subtotal)
    response["total"] = "$" + str(cart.total)
    return jsonify(response)


def checkout_shipping():
    form = AddressForm(request.form)
    user_address = None
    if request.method == "POST":
        if request.form["address_sel"] != "new":
            try:
                user_address = UserAddress.get_by_id(request.form["address_sel"])
                address = client.address.create(
                    verify_strict=True,
                    street1=user_address.address,
                    street2="",
                    city=user_address.city,
                    state=get_state_abbrev(user_address.state),
                    zip=user_address.zip_code,
                    country="US",
                    name=current_user.username,
                    )
                flash(lazy_gettext('Address Verified'), "success")
                print(address)
            except easypost.errors.api.ApiError as error:
                for error in error.errors:   
                    print(error['message'])
                    flash(lazy_gettext(error['message']), "danger")
            
                       
            try:
                stripe.Customer.modify(
                    str(current_user.id),
                    name = current_user.username,
                    address={"city": user_address.city,
                            "line1": user_address.address,
                            "postal_code": user_address.zip_code,
                            "state": user_address.state,
                            "country": "US",
                            },
                    shipping={"address":{
                        "city": user_address.city,
                            "line1": user_address.address,
                            "postal_code": user_address.zip_code,
                            "state": user_address.state,
                            "country": "US",
                                        },
                            "name": user_address.contact_name,
                            },
                    email= current_user.email,   
                    )
            except Exception as e:
                print(e)
                stripe.Customer.create(
                    id=current_user.id,
                    name = current_user.username,
                    address={"city": user_address.city,
                        "line1": user_address.address,
                        "postal_code": user_address.zip_code,
                        "state": user_address.state,
                        },
                    shipping={"address":{
                        "city": user_address.city,
                            "line1": user_address.address,
                            "postal_code": user_address.zip_code,
                            "state": user_address.state,
                            "country": "US",
                                        },
                            "name": user_address.contact_name,
                            },
                    email= current_user.email,
        )
        elif request.form["address_sel"] == "new" and form.validate_on_submit():
            user_address = UserAddress.create(
                contact_name=form.contact_name.data,
                contact_phone=form.contact_phone.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                zip_code=form.zip_code.data,
                user_id=current_user.id,
            )
            try:
                address = client.address.create(
                    verify_strict=True,
                    street1=user_address.address,
                    street2="",
                    city=user_address.city,
                    state=get_state_abbrev(user_address.state),
                    zip=user_address.zip_code,
                    country="US",
                    name=current_user.username,
                    )
                flash(lazy_gettext('Address Verified'), "success")
                print(address)
            except easypost.errors.api.ApiError as error:
                for error in error.errors:   
                    print(error['message'])
                    flash(lazy_gettext(error['message']), "danger")
        try:
            stripe.Customer.modify(
                str(current_user.id),
                name = current_user.username,
                address={"city": user_address.city,
                         "line1": user_address.address,
                         "postal_code": user_address.zip_code,
                         "state": user_address.state,
                         "country": "US",
                         },
                shipping={"address":{
                    "city": user_address.city,
                         "line1": user_address.address,
                         "postal_code": user_address.zip_code,
                         "state": user_address.state,
                         "country": "US",
                                    },
                          "name": user_address.contact_name,
                          },
                email= current_user.email,   
                )
        except Exception as e:
            print(e)
            stripe.Customer.create(
                id=current_user.id,
                name = current_user.username,
                address={"city": user_address.city,
                    "line1": user_address.address,
                    "postal_code": user_address.zip_code,
                    "state": user_address.state,
                    },
                shipping={"address":{
                    "city": user_address.city,
                         "line1": user_address.address,
                         "postal_code": user_address.zip_code,
                         "state": user_address.state,
                         "country": "US",
                                    },
                          "name": user_address.contact_name,
                          },
                email= current_user.email,
    )        
                
        shipping_method = ShippingMethod.get_by_id(request.form["shipping_method"])
        if user_address and shipping_method != None:
            cart = Cart.get_current_user_cart()
            if cart is None:
                abort(403, lazy_gettext("Your Cart is Empty!"))
            cart.update(
                shipping_address_id=user_address.id,
                shipping_method_id=shipping_method.id,
            )
            return redirect(url_for("checkout.checkout_note"))
    flash_errors(form)
    shipping_methods = ShippingMethod.query.all()
    return render_template(
        "checkout/shipping.html", form=form, shipping_methods=shipping_methods
    )


def checkout_note():
    form = NoteForm(request.form)
    voucher_form = VoucherForm(request.form)
    cart = Cart.get_current_user_cart()
    if cart is None:
        abort(403, lazy_gettext("Your Cart is Empty!"))
    else:
        address = (
            UserAddress.get_by_id(cart.shipping_address_id)
            if cart.shipping_address_id
            else None
        )
        shipping_method = (
            ShippingMethod.get_by_id(cart.shipping_method_id)
            if cart.shipping_method_id
            else None
        )
        if form.validate_on_submit():
            order, msg = Order.create_whole_order(cart, form.note.data)
            if order:
                return redirect(order.get_absolute_url())
            else:
                flash(msg, "warning")
                return redirect(url_for("checkout.cart_index"))
        return render_template(
            "checkout/note.html",
            form=form,
            address=address,
            voucher_form=voucher_form,
            shipping_method=shipping_method,
        )


def checkout_voucher():
    voucher_form = VoucherForm(request.form)
    if voucher_form.validate_on_submit():
        voucher = Voucher.get_by_code(voucher_form.code.data)
        cart = Cart.get_current_user_cart()
        err_msg = None
        if voucher:
            try:
                voucher.check_available(cart)
            except Exception as e:
                err_msg = str(e)
        else:
            err_msg = lazy_gettext("Your code is not correct")
        if err_msg:
            flash(err_msg, "warning")
        else:
            cart.voucher_code = voucher.code
            cart.save()
        return redirect(url_for("checkout.checkout_note"))


def checkout_voucher_remove():
    voucher_form = VoucherForm(request.form)
    if voucher_form.validate_on_submit():
        cart = Cart.get_current_user_cart()
        cart.voucher_code = None
        cart.save()
        return redirect(url_for("checkout.checkout_note"))


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("checkout", __name__)

    @bp.before_request
    @login_required
    def before_request():
        """The whole blueprint need to login first"""
        pass

    bp.add_url_rule("/cart", view_func=cart_index)
    bp.add_url_rule(
        "/update_cart/<int:id>", view_func=update_cartline, methods=["POST"]
    )
    bp.add_url_rule("/shipping", view_func=checkout_shipping, methods=["GET", "POST"])
    bp.add_url_rule("/note", view_func=checkout_note, methods=["GET", "POST"])
    bp.add_url_rule("/voucher", view_func=checkout_voucher, methods=["POST"])
    bp.add_url_rule(
        "/voucher/remove", view_func=checkout_voucher_remove, methods=["POST"]
    )

    app.register_blueprint(bp, url_prefix="/checkout")
