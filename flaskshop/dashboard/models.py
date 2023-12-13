from flask import request, url_for, current_app
from datetime import datetime
from flaskshop.constant import SettingValueType
from flaskshop.database import Column, Model, db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from flask_sqlalchemy import SQLAlchemy
import json


def dumpclean(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print(k)
                dumpclean(v)
            else:
                print('%s : %s' % (k, v))
    elif isinstance(obj, list):
        for v in obj:
            if hasattr(v, '__iter__'):
                dumpclean(v)
            else:
                print(v)
    else:
        print(obj)

class DashboardMenu(Model):
    __tablename__ = "management_dashboard"
    title = Column(db.String(255), nullable=False)
    order = Column(db.Integer(), default=0)
    endpoint = Column(db.String(255))
    icon_cls = Column(db.String(255))
    parent_id = Column(db.Integer(), default=0)

    def __str__(self):
        return self.title

    @property
    def children(self):
        return DashboardMenu.query.filter(DashboardMenu.parent_id == self.id).all()

    @classmethod
    def first_level_items(cls):
        return cls.query.filter(cls.parent_id == 0).order_by("order").all()

    def is_active(self):
        if self.endpoint and self.endpoint in request.path:
            return True
        if any((child.is_active() for child in self.children)):
            return True
        return False

    def get_url(self):
        if self.children:
            return "#"
        if self.endpoint:
            return url_for("dashboard." + self.endpoint)


class Setting(Model):
    __tablename__ = "management_setting"
    id = None
    key = Column(db.String(255), primary_key=True)
    value = Column(db.PickleType, nullable=False)
    name = Column(db.String(255), nullable=False)
    description = Column(db.Text, nullable=False)
    value_type = Column(db.Enum(SettingValueType), nullable=False)
    extra = Column(db.PickleType)

    @classmethod
    def get_settings(cls):
        settings = {}
        for s in cls.query.all():
            settings[s.key] = s.value
        return settings

    @classmethod
    def update(cls, settings):
        """Updates the cache and stores the changes in the
        database.
        :param settings: A dictionary with setting items.
        """
        # update the database
        for key, value in settings.items():
            setting = cls.query.filter(Setting.key == key.lower()).first()

            setting.value = value

            db.session.add(setting)
        db.session.commit()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.key}>"

class TicketEntry(Model):
    __tablename__ = "ticket_entry"
    title = Column(db.String(255))
    entry_date = Column(db.Date(), default=db.Date)
    tide_am_pm = Column(db.String(255), default=None)
    set_time = Column(db.Time())
    total_weight = Column(db.Integer(), default=0)
    tickets = db.relationship("Ticket", backref="tickets")


    def __str__(self):
        return self.id
    
    # def __iter__(self):
    #     return iter(self.ticket)

    @property
    def title(self):
        if self.tide_am_pm == 0:
            return str(self.entry_date.strftime("%a, %B %d, %Y")) + ' - ' + str('AM Tide')
        if self.tide_am_pm == 1:
            return str(self.entry_date.strftime("%a, %B %d, %Y")) +'-'+ str('PM Tide')
        return str(self.entry_date) + ' - ' + str(self.tide_am_pm)
    
    @property
    def total_weight(self):
        weight = Ticket.query.filter(Ticket.ticket_entry_id == self.id)
        # complete_weight = Ticket.query()
        we = 0
        for w in weight:
            we += w.weight
        return we




    @property
    def permit_weights(self):
        permits = Ticket.query.filter(Ticket.ticket_entry_id == self.id)
        permits_list = []
        permit_l = []
        we = 0   
        # for p in permits:
        #     if p.permit_num not in permits_list:  
        #         permits_list.append(p.permit_num)
        for w in permits:
                weight = w.weight
                permit = w.permit_num
                permits_list.append((permit, weight))
                permit_l.append(permit)
        permit_totals = {}        
        for weight, value in permits_list:
            total = permit_totals.get(weight, 0) + value
            permit_totals[weight] = total  
        print(dumpclean(permit_totals))
        # for item in permit_totals:
        #     print(item.values())
        return permit_totals
        # for item in permit_l:
        #     # print(item)
        #     print(permit_totals[str(item)])
            
                
        for w in permits_list:
            print(w.permit_num)        
            # if permits.permit_num == w:
        #         we += permits.weight
        #         print(we)
        # return we   
        
        # print(permits_list)     
        for perm in permits_list:
            print(permits.permit_num)
            # if permits.permit_num == perm:
            #     print(perm)
            #     we += perm.weight
            # print(we)
        # return we
        # complete_weight = Ticket.query()
        # we = 0
        # for w in weight:
        #     we += w.weight
        # return we


class Ticket(Model):
    __tablename__ = "ticket_ticket"
    landing_num = Column(db.String(20))
    permit_num = Column(db.String(255))
    weight = Column(db.Integer())
    landing_time = Column(db.Time())
    ticket_notes = Column(db.String(255))
    ticket_entry_id = Column(db.Integer, db.ForeignKey("ticket_entry.id"))


    # def __int__(self):
    #     return self.landing_num
    
    def __int__(self):
        return self.id
    
    def get_total_weight(self):
        return self.weight
    
    @property
    def ticket(self):
        return TicketEntry.get_by_id(self.ticket_entry_id)

    # @property
    # def title(self):
    #     return str(self.entry_date.strftime("%a, %B %d, %Y")) + ' - ' + str('AM Tide')
    
    # def delete(self):
    #     need_del = Ticket.query.filter_by(id=self.id).all()
    #     for item in need_del:
    #         item.delete(commit=False)
    #     db.session.delete(self)
    #     db.session.commit()

    # @classmethod
    # def __flush_delete_event__(cls, target):

    #     super().__flush_delete_event__(target)
    #     target.clear_mc(target)
    #     target.clear_category_cache(target)

    #     if current_app.config["USE_ES"]:
    #         from flaskshop.public.search import Item

    #         Item.delete(target)
    
# from app import admin

# from flask_admin.contrib.sqla import ModelView
# # from flaskshop.dashboard.models import TicketEntry


# admin.add_view(ModelView(TicketEntry, db.session, 'Power Rankings'))