# -*- coding: utf-8 -*-
"""recipe views."""
from flask import abort, Blueprint, flash, jsonify, redirect, render_template, request, url_for
from pluggy import HookimplMarker

from flaskshop.recipe.models import *  # noqa: F403, F401

impl = HookimplMarker("flaskshop")

def recipe():
    return render_template("recipes/test.html")


@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("recipe", __name__)
    bp.add_url_rule("/test", view_func=recipe)
    app.register_blueprint(bp, url_prefix="/recipes")