import os
import os.path as op

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.event import listens_for
from markupsafe import Markup

from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla


# Create application
app = Flask(__name__, static_folder='files')

# set optional bootswatch theme
# see http://bootswatch.com/3/ for available swatches
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'sample_db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Create directory for file fields to use
file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.Unicode(64))
    name = db.Column(db.Unicode(64))
    patronymic = db.Column(db.Unicode(64))
    passport = db.Column(db.Integer)
    comment = db.Column(db.Unicode(256))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Unicode(64))
    last_name = db.Column(db.Unicode(64))
    email = db.Column(db.Unicode(128))
    phone = db.Column(db.Unicode(32))
    city = db.Column(db.Unicode(128))
    country = db.Column(db.Unicode(128))
    notes = db.Column(db.UnicodeText)
    is_admin = db.Column(db.Boolean, default=False)


@listens_for(Image, 'after_delete')
def del_image(mapper, connection, target):
    if target.path:
        # Delete image
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            pass

        # Delete thumbnail
        try:
            os.remove(op.join(file_path,
                              form.thumbgen_filename(target.path)))
        except OSError:
            pass


class ImageView(sqla.ModelView):
    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''

        return Markup('<img src="%s">' % url_for('static',
                                                 filename=form.thumbgen_filename(model.path)))

    column_formatters = {
        'path': _list_thumbnail
    }

    # Alternative way to contribute field is to override it completely.
    # In this case, Flask-Admin won't attempt to merge various parameters for the field.
    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=file_path,
                                      thumbnail_size=(100, 100, True))
    }


class UserView(sqla.ModelView):
    """
    This class demonstrates the use of 'rules' for controlling the rendering of forms.
    """
    form_create_rules = [
        # Header and four fields. Email field will go above phone field.
        rules.FieldSet(('first_name', 'last_name', 'email', 'phone', 'is_admin'), 'Personal'),
        # Separate header and few fields
        rules.Header('Location'),
        rules.Field('city'),
        # String is resolved to form field, so there's no need to explicitly use `rules.Field`
        'country',
        # Show macro that's included in the templates
        rules.Container('rule_demo.wrap', rules.Field('notes'))
    ]

    # Use same rule set for edit page
    form_edit_rules = form_create_rules

    create_template = 'create_user.html'
    edit_template = 'edit_user.html'

    column_descriptions = {
        "is_admin": "Is this an admin user?",
    }


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'

# Create admin
admin = Admin(app, 'Genetico', template_mode='bootstrap4')

# Add views
admin.add_view(ImageView(Image, db.session, name="Исследования и Отчёты"))
admin.add_view(UserView(User, db.session, name="Пользователи"))


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import random
    import string

    db.drop_all()
    db.create_all()

    first_names = [
        'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie','Sophie', 'Mia',
        'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
        'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
    ]
    last_names = [
        'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
        'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
        'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
    ]
    locations = [
        ("Shanghai", "China"),
        ("Istanbul", "Turkey"),
        ("Karachi", "Pakistan"),
        ("Mumbai", "India"),
        ("Moscow", "Russia"),
        ("Sao Paulo", "Brazil"),
        ("Beijing", "China"),
        ("Tianjin", "China"),
        ("Guangzhou", "China"),
        ("Delhi", "India"),
        ("Seoul", "South Korea"),
        ("Shenzhen", "China"),
        ("Jakarta", "Indonesia"),
        ("Tokyo", "Japan"),
        ("Mexico City", "Mexico"),
        ("Kinshasa", "Democratic Republic of the Congo"),
        ("Bangalore", "India"),
        ("New York City", "United States"),
        ("London", "United Kingdom"),
        ("Bangkok", "Thailand"),
        ("Tehran", "Iran"),
        ("Dongguan", "China"),
        ("Lagos", "Nigeria"),
        ("Lima", "Peru"),
        ("Ho Chi Minh City", "Vietnam"),
        ]

    for i in range(len(first_names)):
        user = User()
        user.first_name = first_names[i]
        user.last_name = last_names[i]
        user.email = user.first_name.lower() + "@example.com"
        tmp = ''.join(random.choice(string.digits) for i in range(10))
        user.phone = "(" + tmp[0:3] + ") " + tmp[3:6] + " " + tmp[6::]
        user.city = locations[i][0]
        user.country = locations[i][1]
        db.session.add(user)

    db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        with app.app_context():
            build_sample_db()
        
    # Start app
    app.run(debug=True)
