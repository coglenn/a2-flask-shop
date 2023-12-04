# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, current_app, render_template, request, send_from_directory
from pluggy import HookimplMarker
# from ..app import app
from flaskshop.account.models import User
from flaskshop.extensions import login_manager, sitemapper
from flaskshop.product.models import Product

from .models import Page
from .search import Item
# from .sitemap import sitemap

impl = HookimplMarker("flaskshop")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))

# @sitemapper.include(lastmod="2023-12-01")
def home():
    products = Product.get_featured_product()
    return render_template("public/home.html", products=products)


def style():
    return render_template("public/style_guide.html")


def favicon():
    return send_from_directory("static", "favicon-32x32.png")


def search():
    query = request.args.get("q", "")
    page = request.args.get("page", default=1, type=int)
    if current_app.config["USE_ES"]:
        pagination = Item.new_search(query, page)
    else:
        pagination = Product.query.filter(Product.title.ilike(f"%{query}%")).paginate(
            page
        )
    return render_template(
        "public/search_result.html",
        products=pagination.items,
        query=query,
        pagination=pagination,
    )


def show_page(identity):
    page = Page.get_by_identity(identity)
    return render_template("public/page.html", page=page)

def get_products_list():
    # with app.app_context():
    products = Product.query.all()
    list_products = []
    for product in products:
        list_products.append(product.id)
    return list_products

def sitemap():
    return sitemapper.generate()

# @sitemapper.include()
@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("public", __name__)
    bp.add_url_rule("/", view_func=home)
    bp.add_url_rule("/style", view_func=style)
    bp.add_url_rule("/favicon.ico", view_func=favicon)
    bp.add_url_rule("/search", view_func=search)
    bp.add_url_rule("/sitemap.xml", view_func=sitemap)
    bp.add_url_rule("/page/<identity>", view_func=show_page)
    app.register_blueprint(bp)

sitemapper.add_endpoint("public.home")
sitemapper.add_endpoint("public.show_page", url_variables={"identity": ['about']},)
sitemapper.add_endpoint("product.show", url_variables={"id": [129, 130, 131, 132, 133, 134]},)
# sitemapper.add_endpoint("public.show_page", identity='about')