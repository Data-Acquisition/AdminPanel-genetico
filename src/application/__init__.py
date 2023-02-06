from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
import flask_admin
from flask_admin import helpers as admin_helpers
from application.views import *
from application.routes.admin import admin_routing


app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

from application.models import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


admin = flask_admin.Admin(
    app,
    'GENETICO',
    base_template='my_master.html',
    template_mode='bootstrap4',
)



# admin.add_view(MyModelView(Role, db.session, menu_icon_type='fa',
#                         menu_icon_value='fa-server', name="Roles"))
admin.add_view(UserView(User, db.session, menu_icon_type='fa',
                        menu_icon_value='fa-users', name="Пользователи"))
admin.add_view(ResearchView(Research, db.session, menu_icon_type='fa',
                            menu_icon_value='fa-connectdevelop',
                            name="Исследования и отчёты"))

@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


app.register_blueprint(admin_routing)
