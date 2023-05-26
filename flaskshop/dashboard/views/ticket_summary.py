from datetime import datetime

from sqlalchemy import func, create_engine
from sqlalchemy.orm import sessionmaker
from flask import render_template

from flaskshop.account.models import User
from flaskshop.settings import DBConfig
from flaskshop.extensions import db
from flaskshop.dashboard.models import (
    Ticket,
    TicketEntry,

)

engine = create_engine(DBConfig.db_uri)

Session = sessionmaker(bind=engine)
session = Session()

def index_ticket():
    def get_today_num(model):
        target = db.cast(datetime.now(), db.DATE)
        which = db.cast(model.created_at, db.DATE)
        return model.query.filter(which == target).count()

    # def get_today_num(model):
    #     target = db.cast(datetime.now(), db.DATE)
    #     which = db.cast(model.created_at, db.DATE)
    #     return model.query.filter(which == target).count()

    tickets = get_today_num(Ticket)

    weight = Ticket.query.all()
    complete_weight = Ticket.query()
    we = 0
    for w in weight:
        we += w.weight


    tot_weight = session.query(func.sum(Ticket.weight).label("total_weight"))
    max_deliv = session.query(func.max(Ticket.weight).label("Max_delivery")).first()
    max_deliv = max_deliv[0]
    print(max_deliv)                

    context = {
        "Tides_total": TicketEntry.query.count(),
        "deliveries_today": tickets,
        "users_total": User.query.count(),
        "total_deliveries": Ticket.query.count(),
        # "users_today": get_today_num(User),
        # "order_unfulfill": get_order_status(OrderStatusKinds.unfulfilled.value),
        # "order_fulfill": get_order_status(OrderStatusKinds.processing.value),
        # "onsale_products_count": onsale_products_count,
        "total_weight": we,
        "max_deliv": max_deliv,
        # "order_events": OrderEvents,
    }
    return render_template("ticket_sum.html", **context)
