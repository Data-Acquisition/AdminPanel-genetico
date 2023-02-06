import os
import os.path as op
import random
from application.views.base_view import MyModelView
from markupsafe import Markup
from flask import appcontext_popped, url_for
from flask_admin import form
from application.ml.test import Predict, ModelFit
from wtforms import HiddenField

# file_path = op.join(op.dirname(__file__), 'files')
# try:
#     os.mkdir(file_path)
# except OSError:
#     pass

file_path = os.path.abspath(os.path.dirname(__name__))

class ResearchView(MyModelView):
    column_exclude_list = ('patronymic', 'passport',)
    # form_excluded_columns = ('PP', 'DP', 'DS', 'DC',)
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
                                      thumbnail_size=(100, 100, True)),
        'diff_p': HiddenField('diff_p'),
        'mix_p': HiddenField('mix_p'),
        'den_p': HiddenField('den_p'),
        'prol': HiddenField('prol'),

    }
    
    def add_metrics(self, _form):
        try:
            static_image = _form.path.data.stream.read()
            result = Predict(static_image, ModelFit)
            # формула неправильная, хотел просто прsоверить, чтобы хоть что-то заходило в бд
            print(result)
            diffusion = len(result['Diffuse'])
            mixed = len(result['Mixed'])
            dense = len(result['Dense'])
            print(diffusion)
            print(mixed)
            print(dense)

            total = diffusion+mixed+dense
            diffusion_percentage = (diffusion/total)*100
            mixed_percentage = (mixed/total)*100
            dense_percentage = (dense/total)*100
            proliferation = (diffusion_percentage + 2 *
                             mixed_percentage + 3*dense_percentage)/100
            print(proliferation)
            _form.diff_p.data = diffusion_percentage
            _form.mix_p.data = mixed_percentage
            _form.den_p.data = dense_percentage
            _form.prol.data = proliferation
        except Exception as ex:
            print(ex)
            pass

        return _form
      

    def create_form(self, obj=None):
        return self.add_metrics(
            super(ResearchView, self).create_form(obj)
        )
    
    def edit_form(self, obj=None):
        return self.add_metrics(
            super(ResearchView, self).edit_form(obj)
        )
