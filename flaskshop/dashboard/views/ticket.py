from flask import redirect, render_template, request, url_for, flash
from flask_babel import lazy_gettext


from flaskshop.dashboard.utils import save_img_file, wrap_partial, item_del

from flaskshop.dashboard.forms import (
    TicketForm,
    TicketEntryForm,
    TicketCreateForm,
)
from flaskshop.dashboard.models import (
    Ticket,
    TicketEntry,

)




def tickets():
    page = request.args.get("page", type=int, default=1)
    query = TicketEntry.query

    # on_sale = request.args.get("sale", type=int)
    # if on_sale is not None:
    #     query = query.filter_by(on_sale=on_sale)
    # category = request.args.get("category", type=int)
    # if category:
    #     query = query.filter_by(category_id=category)
    # title = request.args.get("title", type=str)
    # if title:
    #     query = query.filter(Product.title.like(f"%{title}%"))
    # created_at = request.args.get("created_at", type=str)
    # if created_at:
    #     query = query.filter(Product.created_at >= created_at)
    # ended_at = request.args.get("ended_at", type=str)
    # if ended_at:
    #     query = query.filter(Product.created_at <= ended_at)

    pagination = query.paginate(page, 10)
    props = {
        "id": lazy_gettext("ID"),
        "title": lazy_gettext("Title"),
        "entry_date": lazy_gettext("Date"),
        "total_weight": lazy_gettext("Wieght"),
    }
    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,

    }
    return render_template("ticket/list.html", **context)


def ticket_detail(id):
    ticket = TicketEntry.get_by_id(id)
    order = Ticket.query.filter_by(ticket_entry_id=id) 
    return render_template("dashboard/ticket/detail.html", order=order, ticket=ticket)


def ticket_manage(id=None):
    if id:
        ticket = TicketEntry.get_by_id(id)
        form = TicketEntryForm(obj=ticket)
        # weight = Ticket.query.filter(Ticket.ticket_entry_id == id)
        # we = 0
        # for w in weight:
        #     we += w.weight
        # print(we)
        # tide = ticket.tide_am_pm
    else:
        form = TicketEntryForm()
        tide = request.args.get("tide_type")
        print(tide)
        ticket = TicketEntry(tide_am_pm=tide)
    if form.validate_on_submit():
        form.populate_obj(ticket)
        ticket.save()
        flash(lazy_gettext("Ticket saved."), "success")
        return redirect(url_for("dashboard.ticket_detail", id=ticket.id))
    context = {"form": form}
    return render_template("ticket/ticket.html", **context)


ticket_entry_del = wrap_partial(item_del, TicketEntry)

def ticket_create_step1():
    form = TicketCreateForm()
    if form.validate_on_submit():
        return redirect(
            url_for(
                "dashboard.ticket_manage",
                tide_type=form.tide_am_pm.data,
            )
        )
    return render_template(
        "general_edit.html", form=form, title=lazy_gettext("Ticket Entry Step 1")
    )


def ticket_entry_manage(id=None):
    if id:
        ticket_entry = Ticket.get_by_id(id)
        form = TicketForm(obj=ticket_entry)
    else:
        ticket_entry = Ticket()
        form = TicketForm()
    if form.validate_on_submit():
        form.populate_obj(ticket_entry)
        # ticket_entry.update_images(form.images.data)
        # del form.images

        ticket_id = request.args.get('ticket_id')
        # ticket_id = request.args.get('ticket_entry_id')
        print(ticket_id)
        if ticket_id:
            ticket_entry.ticket_entry_id = ticket_id
        # ticket_entry_items = Ticket.get_by_id(ticket_id)
  
        # ticket_entry.sku = str(ticket_entry.product_id) + "-" + str(form.sku_id.data)
        

        # upload_imgs = request.files.getlist("new_images")
        # for img in upload_imgs:
        #     # request.files.getlist always not return empty, even not upload files
        #     if not img.filename:
        #         continue
        #     ProductImage.create(
        #         image=save_img_file(img),
        #         product_id=product.id,
        #     )
        
        ticket_entry.save()
        try:
            ticket_enter = Ticket.get_by_id(id).ticket_entry_id
            print(ticket_enter)
        except AttributeError:
            ticket_enter = request.args.get('ticket_id')
        # if Ticket.get_by_id(id).id is None:
        #     ticket_enter = request.args.get('ticket_id')
        # else:
        #     ticket_enter = Ticket.get_by_id(id).id
        # print(ticket_enter)
        flash(lazy_gettext("ticket_entry saved."), "success")
        return redirect(url_for("dashboard.ticket_detail", id=ticket_enter))
    return render_template(
        "general_edit.html", form=form, title=lazy_gettext("ticket_entry")
    )


ticket_del = wrap_partial(item_del, Ticket)