from flask import redirect, render_template, request, url_for, flash

from flask import Blueprint
from pluggy import HookimplMarker

from .models import *  # noqa: F403, F401
from .forms import *  # noqa: F403, F401
impl = HookimplMarker("flaskshop")


@impl
def flaskshop_load_blueprints(app):
    ticket = Blueprint("ticket", __name__)
    app.register_blueprint(ticket, url_prefix="/ticket")

def ticket_detail(id):
    ticket = ticket.get_by_id(id)
    return render_template("ticket/detail.html", ticket=ticket)


def ticket_manage(id=None):
    if id:
        ticket = Ticket.get_by_id(id)
        form = TicketForm(obj=ticket)
    else:
        form = TicketForm()
        ticket = Ticket()
    if form.validate_on_submit():
        form.populate_obj(ticket)
        ticket.save()
        flash(lazy_gettext("Ticket saved."), "success")
        return redirect(url_for("ticket.ticket_detail", id=ticket.id))
    context = {"form": form}
    return render_template("ticket/ticket.html", **context)


product_del = wrap_partial(item_del, Product)

def product_create_step1():
    form = ticket_entry_form()
    form.product_type_id.choices = [(p.id, p.title) for p in ProductType.query.all()]
    if form.validate_on_submit():
        return redirect(
            url_for(
                "dashboard.product_manage",
                product_type_id=form.product_type_id.data,
            )
        )
    return render_template(
        "general_edit.html", form=form, title=lazy_gettext("Product Step 1")
    )


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("ticket", __name__)
    bp.add_url_rule("/<int:id>", view_func=show)
    bp.add_url_rule("/api/variant_price/<int:id>", view_func=variant_price)
    bp.add_url_rule("/<int:id>/add", view_func=product_add_to_cart, methods=["POST"])
    bp.add_url_rule("/category/<int:id>", view_func=show_category)
    bp.add_url_rule("/collection/<int:id>", view_func=show_collection)

    app.register_blueprint(bp, url_prefix="/ticket")