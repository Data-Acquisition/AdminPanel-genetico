from flask import Blueprint
from flask import render_template

admin_routing = Blueprint("base_admin", __name__)


@admin_routing.route('/')
def index():
    return render_template('index.html')
