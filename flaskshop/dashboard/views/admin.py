# from app import db, admin, create_app

# from flask_admin.contrib.sqla import ModelView, BaseView, expose
# from flaskshop.dashboard.models import TicketEntry


# class MyView(BaseView):
#     # @expose('/')
#     def index(self):
#         return self.render('index.html')

# # admin.add_view(MyView(name='Hello'))
# admin.add_view(ModelView(TicketEntry, db.session, 'Power Rankings'))