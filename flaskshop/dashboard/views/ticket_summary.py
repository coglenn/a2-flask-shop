from datetime import datetime, date


from sqlalchemy import func, create_engine, extract 
from sqlalchemy.orm import sessionmaker
from flask import render_template

from flaskshop.account.models import User
from flaskshop.settings import DBConfig
from flaskshop.extensions import db
from flaskshop.dashboard.models import (
    Ticket,
    TicketEntry,

)
from pprint import pprint
from noaa_coops import Station
import json
import pandas as pd
import sqlalchemy


engine = create_engine(DBConfig.db_uri)

Session = sessionmaker(bind=engine)
session = Session()

def Average(lst):
    return sum(lst) / len(lst)

def index_ticket():
    
    # by_year = Ticket.query.filter(extract('year', Ticket.) == 2016, extract('month', Record.dt) == 10)
    
    def get_today_num(model):
        target = db.cast(datetime.now(), db.DATE)
        which = db.cast(model.created_at, db.DATE)
        return model.query.filter(which == target).count()


    tickets = get_today_num(Ticket)

    weight = Ticket.query.all()
    we = 0
    colt_deliv_list = [] 
    permit_total_list = [] 
    # permit_list = []
    # for permit_number in weight:
    #     permit_list.append(permit_number.permit_num)
    # permit_list = list(set(permit_list))
    # print(permit_list)
    weight_list = []
    season_weight = 0
    if weight is not None:
        for w in weight:
            we += w.weight
            
            if w.ticket_entry_id != 0:
                date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
                # if date.entry_date.year == 2022:
                weight = w.weight
                date = str(date.entry_date)
                colt_deliv_list.append((date, weight))
                permit = w.permit_num
                permit_total_list.append((permit, weight))
                if w.weight != 0:
                    season_weight += w.weight
                    weight_list.append(w.weight)
                    season_max = w.weight
    print(max(weight_list))
                        # average_deliv = round(we/count(str(w.weight)))
                    # average_deliv = round(we/db.session.query(Ticket).filter(Ticket.weight.like(not 0), Ticket.created_at.year.like(2023)).count())
    totals = {}
    for total_weight, value in colt_deliv_list:
        total = totals.get(total_weight, 0) + value
        totals[total_weight] = total
    labels = [row[0] for row in totals.items()]
    values = [row[1] for row in totals.items()]
    values_total = [row[1] for row in totals.items()]
    # print(labels)   
    # print(colt_deliv_list) 
    # complete_weight = Ticket.query()
    # we = 0
    # if weight is not None:
    #     for w in weight:
    #         we += w.weight
    # if weight is not None:
    #     if weight.ticket_entry_id != 0:
    #         date = TicketEntry.query.filter(TicketEntry.id == weight.ticket_entry_id).first()
    #         if date.entry_date.year == 2023:
    #             average_deliv = round(we/Ticket.query.filter(Ticket.weight != 0 ).count())
    #             tot_weight = session.query(func.sum(Ticket.weight).label("total_weight"))
    #             max_deliv = session.query(func.max(Ticket.weight).label("Max_delivery")).first()
    #             max_deliv = max_deliv[0]
    average_deliv = round(we/Ticket.query.filter(Ticket.weight != 0 ).count())
    tot_weight = session.query(func.sum(Ticket.weight).label("total_weight"))
    # max_deliv = session.query(func.max(Ticket.weight).label("Max_delivery")).first()
    # max_deliv = max_deliv[0]     
    max_deliv = 0       
    # weight_graph = [row[0] for row in weight.weight]
    # print(weight_graph)
    
    
# horizontal bar graph
    # weight = Ticket.query.all()
    # permit_total_list = [] 
    # if weight is not None:
    #     for w in weight:
    #         if w.ticket_entry_id != 0:
    #             weight = w.weight
    #             permit = w.permit_num
    #             permit_total_list.append((permit, weight))
    permit_totals = {}
    for weight, value in permit_total_list:
        total = permit_totals.get(weight, 0) + value
        permit_totals[weight] = total
    permit_labels = [row[0] for row in permit_totals.items()]
    permit_values = [row[1] for row in permit_totals.items()] 
                    

    context = {
        "Tides_total": TicketEntry.query.count(),
        "deliveries_today": tickets,
        "users_total": User.query.count(),
        "total_deliveries": Ticket.query.filter(Ticket.weight != 0 ).count(),
        "average_deliveries": average_deliv,
        "total_weight": we,
        "max_deliv": max_deliv,
        "largest_weight": max(values_total),
        "season_weight": season_weight,
        "season_max": max(weight_list),        
        # "largest_weight": 0,
        'labels': labels,
        'values': values,
        'permit_labels': permit_labels,
        'permit_values': permit_values,
    }
    return render_template("ticket_sum.html", **context)


def ticket_graph():
    tickets = sqlalchemy.extract('year', TicketEntry.entry_date) == 2023
    date_entered = TicketEntry.query.filter_by(entry_date=tickets).all()
    transactions = db.session.query (TicketEntry.entry_date, func.sum(Ticket.weight)).group_by(TicketEntry.entry_date).all()
    for t in transactions:
        print(t)
    weight = Ticket.query.all()
    # permit_list = []
    # for permit_number in weight:
    #     permit_list.append(permit_number.permit_num)
    # permit_list = list(set(permit_list))
    we = 0
    colt_deliv_list = [] 
    if weight is not None:
        for w in weight:
            we += w.weight
            if w.ticket_entry_id != 0:
                # if w.permit_num == 'Colt - 60021C':
                date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
                weight = w.weight
                date = str(date.entry_date)
                colt_deliv_list.append((date, weight))
                # colt_deliv_list.append(str(date.entry_date))
                # colt_deliv_list.append(weight)
                # print(date.entry_date)
    totals = {}
    for weight, value in colt_deliv_list:
        total = totals.get(weight, 0) + value
        totals[weight] = total
    labels = [row[0] for row in totals.items()]
    values = [row[1] for row in totals.items()]
    values_total = [row[1] for row in totals.items()]
    
    weight = Ticket.query.all()
    permit_total_list = [] 
    if weight is not None:
        for w in weight:
            we += w.weight
            if w.ticket_entry_id != 0:
                weight = w.weight
                permit = w.permit_num
                permit_total_list.append((permit, weight))
    permit_totals = {}
    for weight, value in permit_total_list:
        total = permit_totals.get(weight, 0) + value
        permit_totals[weight] = total
    permit_labels = [row[0] for row in permit_totals.items()]
    permit_values = [row[1] for row in permit_totals.items()]    
    
    
    # colt_deliv_list = []
    # permit_weight = 0
    # weight = Ticket.query.all()
    # if weight is not None:
    #     for w in weight:
    #         permit_weight += w.weight
    #         if w.ticket_entry_id != 0:   
    #             if w.permit_num == 'Colt - 60021C':
    #                 date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
    #                 weight = w.weight
    #                 date = str(date.entry_date)
    #                 colt_deliv_list.append((date, weight))
    # colt_totals = {}
    # for weight, value in colt_deliv_list:
    #     total = colt_totals.get(weight, 0) + value
    #     colt_totals[weight] = total
    # c_labels = [row[0] for row in colt_totals.items()]
    # c_values = [row[1] for row in colt_totals.items()]
    
    # harlan_deliv_list = []
    # permit_weight = 0
    # weight = Ticket.query.all()
    # if weight is not None:
    #     for w in weight:
    #         permit_weight += w.weight
    #         if w.ticket_entry_id != 0:   
    #             if w.permit_num == 'Harlan - 61279W':
    #                 date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
    #                 weight = w.weight
    #                 date = str(date.entry_date)
    #                 harlan_deliv_list.append((date, weight))
    # harlan_totals = {}
    # for weight, value in harlan_deliv_list:
    #     total = harlan_totals.get(weight, 0) + value
    #     harlan_totals[weight] = total
    # h_labels = [row[0] for row in harlan_totals.items()]
    # h_values = [row[1] for row in harlan_totals.items()]
    
    # jed_deliv_list = []
    # permit_weight = 0
    # weight = Ticket.query.all()
    # if weight is not None:
    #     for w in weight:
    #         permit_weight += w.weight
    #         if w.ticket_entry_id != 0:   
    #             if w.permit_num == 'Jed - 61279W':
    #                 date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
    #                 weight = w.weight
    #                 date = str(date.entry_date)
    #                 jed_deliv_list.append((date, weight))
    # jed_totals = {}
    # for weight, value in jed_deliv_list:
    #     total = jed_totals.get(weight, 0) + value
    #     jed_totals[weight] = total
    # j_labels = [row[0] for row in jed_totals.items()]
    # j_values = [row[1] for row in jed_totals.items()]

    
    context = {

        'labels': labels,
        'values': values,
        'permit_labels': permit_labels,
        'permit_values': permit_values,

        # 'c_labels': c_labels,
        # 'c_values': c_values,
        # 'h_labels': h_labels,
        # 'h_values': h_values,
        # 'j_labels': j_labels,
        # 'j_values': j_values,
    }
    # for value in values:
         
    # print(colt_deliv_list) 
    return render_template("ticket_graph.html", **context)



def tide_graph():
    be_date = datetime.now()
    begin_date = str(be_date.date()).replace('-','')
    egegik = Station(id="9464881")
    df_water_levels = egegik.get_data(
    begin_date=begin_date,
    end_date="2023731",
    product="predictions",
    interval='hilo',
    datum="MLLW",
    units="english",
    time_zone="lst_ldt")
    
    # df_water_levels = df_water_levels.head(4)

    # df_water_levels.loc[(df_water_levels['index'] == begin_date)]
    df = df_water_levels.filter(like = str(be_date.date()), axis=0)
    df = df.reset_index(inplace=True)
    df = df = df.rename(columns = {'index':'t'})
    # df = df.reset_index(inplace=True)
    # df = df.set_index([pd.Index([1, 2, 3, 4])])
    print(df)
    weight = Ticket.query.all()
    # permit_list = []
    # for permit_number in weight:
    #     permit_list.append(permit_number.permit_num)
    # permit_list = list(set(permit_list))
    we = 0
    colt_deliv_list = [] 
    if weight is not None:
        for w in weight:
            we += w.weight
            if w.ticket_entry_id != 0:
                # if w.permit_num == 'Colt - 60021C':
                date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
                weight = w.weight
                date = str(date.entry_date)
                colt_deliv_list.append((date, weight))
                # colt_deliv_list.append(str(date.entry_date))
                # colt_deliv_list.append(weight)
                # print(date.entry_date)
    totals = {}
    for weight, value in colt_deliv_list:
        total = totals.get(weight, 0) + value
        totals[weight] = total
    labels = [row[0] for row in totals.items()]
    values = [row[1] for row in totals.items()]
    values_total = [row[1] for row in totals.items()]
    
    weight = Ticket.query.all()
    permit_total_list = [] 
    if weight is not None:
        for w in weight:
            we += w.weight
            if w.ticket_entry_id != 0:
                weight = w.weight
                permit = w.permit_num
                permit_total_list.append((permit, weight))
    permit_totals = {}
    for weight, value in permit_total_list:
        total = permit_totals.get(weight, 0) + value
        permit_totals[weight] = total
    permit_labels = [row[0] for row in permit_totals.items()]
    permit_values = [row[1] for row in permit_totals.items()]    
    
    
    # colt_deliv_list = []
    # permit_weight = 0
    # weight = Ticket.query.all()
    # if weight is not None:
    #     for w in weight:
    #         permit_weight += w.weight
    #         if w.ticket_entry_id != 0:   
    #             if w.permit_num == 'Colt - 60021C':
    #                 date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
    #                 weight = w.weight
    #                 date = str(date.entry_date)
    #                 colt_deliv_list.append((date, weight))
    # colt_totals = {}
    # for weight, value in colt_deliv_list:
    #     total = colt_totals.get(weight, 0) + value
    #     colt_totals[weight] = total
    # c_labels = [row[0] for row in colt_totals.items()]
    # c_values = [row[1] for row in colt_totals.items()]
    
    # harlan_deliv_list = []
    # permit_weight = 0
    # weight = Ticket.query.all()
    # if weight is not None:
    #     for w in weight:
    #         permit_weight += w.weight
    #         if w.ticket_entry_id != 0:   
    #             if w.permit_num == 'Harlan - 61279W':
    #                 date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
    #                 weight = w.weight
    #                 date = str(date.entry_date)
    #                 harlan_deliv_list.append((date, weight))
    # harlan_totals = {}
    # for weight, value in harlan_deliv_list:
    #     total = harlan_totals.get(weight, 0) + value
    #     harlan_totals[weight] = total
    # h_labels = [row[0] for row in harlan_totals.items()]
    # h_values = [row[1] for row in harlan_totals.items()]
    
    # jed_deliv_list = []
    # permit_weight = 0
    # weight = Ticket.query.all()
    # if weight is not None:
    #     for w in weight:
    #         permit_weight += w.weight
    #         if w.ticket_entry_id != 0:   
    #             if w.permit_num == 'Jed - 61279W':
    #                 date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
    #                 weight = w.weight
    #                 date = str(date.entry_date)
    #                 jed_deliv_list.append((date, weight))
    # jed_totals = {}
    # for weight, value in jed_deliv_list:
    #     total = jed_totals.get(weight, 0) + value
    #     jed_totals[weight] = total
    # j_labels = [row[0] for row in jed_totals.items()]
    # j_values = [row[1] for row in jed_totals.items()]

    
    context = {

        'labels': labels,
        'values': values,
        'permit_labels': permit_labels,
        'permit_values': permit_values,

        # 'c_labels': c_labels,
        # 'c_values': c_values,
        # 'h_labels': h_labels,
        # 'h_values': h_values,
        # 'j_labels': j_labels,
        # 'j_values': j_values,
    }
    # for value in values:
         
    # print(colt_deliv_list) 
    return render_template("tide_graph.html", **context)

def index_ticket_23():
    
    # by_year = Ticket.query.filter(extract('year', Ticket.) == 2016, extract('month', Record.dt) == 10)
    
    def get_today_num(model):
        target = db.cast(datetime.now(), db.DATE)
        which = db.cast(model.created_at, db.DATE)
        return model.query.filter(which == target).count()


    tickets = get_today_num(Ticket)

    weight = Ticket.query.all()
    weigh = TicketEntry.query.all()
    counter = 0
    entry_23 = 0
    for entry in weigh:
        # print(entry.entry_date)
        if entry.entry_date.year == 2023:
            entry_23 += 1
            for ticket in entry.tickets:
                counter += 1
    we = 0
    colt_deliv_list = [] 
    permit_total_list = [] 
    weight_list = []
    season_weight = 0
    permit_line = []
    if weight is not None:
        for w in weight:
            we += w.weight
            if w.ticket_entry_id != 0:
                date = TicketEntry.query.filter(TicketEntry.id == w.ticket_entry_id).first()
                if date.entry_date.year == 2023:
                    weight = w.weight
                    date = str(date.entry_date.strftime('%m-%d') )
                    colt_deliv_list.append((date, weight))
                    permit = w.permit_num
                    permit_total_list.append((permit, weight))
                    permit_line.append((date, permit, weight))
                    if w.weight != 0:
                        season_weight += w.weight
                        weight_list.append(w.weight)
    # print(max(weight_list))
                        # average_deliv = round(we/count(str(w.weight)))
                    # average_deliv = round(we/db.session.query(Ticket).filter(Ticket.weight.like(not 0), Ticket.created_at.year.like(2023)).count())
    totals = {}
    for total_weight, value in colt_deliv_list:
        # print(total_weight)
        total = totals.get(total_weight, 0) + value
        totals[total_weight] = total
    labels = [row[0] for row in totals.items()]
    values = [row[1] for row in totals.items()]
    values_total = [row[1] for row in totals.items()]
    print(values_total)


    # max_deliv = session.query(func.max(Ticket.weight).label("Max_delivery")).first()
    # max_deliv = max_deliv[0]
    max_deliv = 0            

    permit_totals = {}
    for weight, value in permit_total_list:
        total = permit_totals.get(weight, 0) + value
        permit_totals[weight] = total
    permit_labels = [row[0] for row in permit_totals.items()]
    permit_values = [row[1] for row in permit_totals.items()] 
    print(permit_values)
    
    line_totals = {}
    for date, permit, value in permit_line:
        total = line_totals.get(date, 0) + value
        # date = line_totals.get(date)
        line_totals[permit] = total
        print(date)
        # line_totals[date] = date
    permit_num_labels = [row[0] for row in line_totals.items()]    
    line_labels = [row[1] for row in line_totals.items()]
    p_values = [row[1] for row in line_totals.items()] 
    print(line_totals)

    context = {
        "Tides_total": entry_23,
        "deliveries_today": tickets,
        # "users_total": User.query.count(),
        "total_deliveries": counter,
        "average_deliveries": Average(weight_list),
        "total_weight": season_weight,
        "max_deliv": max_deliv,
        "largest_weight": max(values_total),
        "season_weight": season_weight,
        "season_max": max(weight_list),        
        # "largest_weight": 0,
        'labels': labels,
        'values': values,
        'permit_labels': permit_labels,
        'permit_values': permit_values,
        'permit_num_labels': permit_num_labels,
        'line_labels': line_labels,
        'p_values': p_values,
    }
    return render_template("ticket_sum_23.html", **context)