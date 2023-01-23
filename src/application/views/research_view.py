import os
import os.path as op
from application.views.base_view import MyModelView
from markupsafe import Markup
from flask import url_for
from flask_admin import form

# file_path = op.join(op.dirname(__file__), 'files')
# try:
#     os.mkdir(file_path)
# except OSError:
#     pass

file_path = os.path.abspath(os.path.dirname(__name__))

class ResearchView(MyModelView):
    column_exclude_list = ('patronymic', 'passport',)
    form_excluded_columns = ('PP', 'DP', 'DS', 'DC',)
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
                                      base_path=os.path.join(file_path, 'application/static'),
                                      thumbnail_size=(100, 100, True))
    }