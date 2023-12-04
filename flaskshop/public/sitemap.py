# from flask import Blueprint, current_app
# from flaskshop.extensions import sitemapper
# # from flaskshop.utils import get_products_list
# from flask.cli import with_appcontext
# from flaskshop.product.models import Product

# # from pluggy import HookimplMarker

# # impl = HookimplMarker("flaskshop")

# def sitemap():
#   return sitemapper.generate()


# def get_products_list():
#   with app.app_context():
#     products = Product.query.all()
#     list_products = []
#     for product in products:
#       list_products.append(product.id)
#     return list_products
  

# # @impl
# # def flaskshop_load_blueprints(app):
# #     bp = Blueprint("site", __name__)
# #     bp.add_url_rule("/sitemap.xml", view_func=sitemap)
# #     app.register_blueprint(bp)
    
# sitemapper.add_endpoint("public.home")
# sitemapper.add_endpoint("public.show_page", url_variables={"identity": ['about']},)
# sitemapper.add_endpoint("product.show", url_variables={"id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 71]},)