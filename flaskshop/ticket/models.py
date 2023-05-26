import random
import string
from datetime import datetime
from decimal import Decimal

from flaskshop.constant import DiscountValueTypeKinds, VoucherTypeKinds
from flaskshop.corelib.mc import rdb
from flaskshop.database import Column, Model, db
from flaskshop.product.models import MC_KEY_PRODUCT_DISCOUNT_PRICE, Category, Product

# MC_KEY_SALE_PRODUCT_IDS = "discount:sale:{}:product_ids"


class TicketEntry(Model):
    __tablename__ = "ticket_entry"
    entry_date = Column(db.Date(), default=db.Date)
    tide_am_pm = Column(db.Boolean(), default=None)
    total_weight = Column(db.Integer(), default=0)
    ticket_id = Column(db.Integer())

    def __str__(self):
        return self.id

    @property
    def type_human(self):
        return VoucherTypeKinds(int(self.type_)).name


class Ticket(Model):
    __tablename__ = "ticket_ticket"
    landing_num = Column(db.Integer())
    permit_num = Column(db.String(255))
    weight = Column(db.String(16), unique=True)
    landing_time = Column(db.Datetime())
    ticket_notes = Column(db.String(255))


    def __str__(self):
        return self.landing_num
    
    def get_total_weight(self):
        return self.weight

