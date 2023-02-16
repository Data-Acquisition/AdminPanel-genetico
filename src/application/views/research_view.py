import os
import os.path as op
import random

import numpy as np
from application.views.base_view import MyModelView
from markupsafe import Markup
from flask import appcontext_popped, url_for
from flask_admin import form
from application.ml.test import Predict, ModelFit, split_cups
from application.ml.utils import join_images, image_to_grayscale
from wtforms import HiddenField
import io
import cv2

file_path = os.path.abspath(os.path.dirname(__name__))


def namegen(obj, file_data):
    name, _ = op.splitext(file_data.filename)
    return ('%s.jpg' % name)


def thumb_gen(filename):
    name, _ = op.splitext(filename)
    return ('%s_thumb.jpg' % name)


def transliterate(text):
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ya', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'yo',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CH', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '', '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': ''}
    # Циклически заменяем все буквы в строке
    for key in slovar:
        text = text.replace(key, slovar[key])
    return text


class ResearchView(MyModelView):
    column_exclude_list = ('patronymic', 'passport', 'first_cup', 'second_cup')
    column_searchable_list = ['passport', 'last_name', 'name']

    # form_excluded_columns = ('PP', 'DP', 'DS', 'DC',)

    def _list_thumbnail(view, context, model, name):
        if not model.path:
            return ''
        return Markup(
            '<img src="%s" onclick=\'window.open("%s","targetWindow", "toolbar=no, location=no, status=no, menubar=no, scrollbars=yes, resizable=yes, width=1090px, height=550px, top=25px left=120px"); return false;\'>' % (
                url_for('static', filename=form.thumbgen_filename(model.path)), url_for('static', filename=model.path)))

    def _list_thumbnail_first_cup(view, context, model, name):
        if not model.path:
            return ''
        return Markup(
            '<img src="%s" onclick=\'window.open("%s","targetWindow", "toolbar=no, location=no, status=no, menubar=no, scrollbars=yes, resizable=yes, width=1090px, height=550px, top=25px left=120px"); return false;\'>' % (
                url_for('static', filename=form.thumbgen_filename(
                    model.first_cup)),
                url_for('static', filename=model.first_cup)))

    def _list_thumbnail_second_cup(view, context, model, name):
        if not model.path:
            return ''
        return Markup(
            '<img src="%s" onclick=\'window.open("%s","targetWindow", "toolbar=no, location=no, status=no, menubar=no, scrollbars=yes, resizable=yes, width=1090px, height=550px, top=25px left=120px"); return false;\'>' % (
                url_for('static', filename=form.thumbgen_filename(
                    model.second_cup)),
                url_for('static', filename=model.second_cup)))

    column_formatters = {
        'path': _list_thumbnail,
        'first_cup': _list_thumbnail_first_cup,
        'second_cup': _list_thumbnail_second_cup
    }

    form_extra_fields = {
        'path': form.ImageUploadField('Image',
                                      base_path=os.path.join(
                                          file_path, 'application/static'), namegen=namegen, thumbgen=thumb_gen,
                                      thumbnail_size=(100, 100, True)),
        'first_cup': HiddenField('first_cup'),
        'second_cup': HiddenField('second_cup'),
        'diff_p': HiddenField('diff_p'),
        'mix_p': HiddenField('mix_p'),
        'den_p': HiddenField('den_p'),
        'prol': HiddenField('prol'),
        'regen_p': HiddenField('regen_p'),

    }

    def add_metrics(self, _form):
        try:
            static_image = _form.path.data.stream.read()
            print('прочитал картинку')
            first_cup, second_cup = split_cups(static_image)
            first_cup_result_image, first_cup_results = Predict(first_cup, ModelFit)
            second_cup_result_image, second_cup_results = Predict(second_cup, ModelFit)
            img_box = join_images(first_cup_result_image, second_cup_result_image)
            first_cup_g = image_to_grayscale(first_cup)
            second_cup_g = image_to_grayscale(second_cup)
            result = {k: v + second_cup_results[k] for k, v in first_cup_results.items()}
            name_trans = transliterate(_form.path.data.filename.split('.')[0])
            first_cup_file_name = name_trans + '_first_cup' + '.' + \
                                  _form.path.data.filename.split('.')[1]
            th_first_cup_file_name = name_trans + '_first_cup_thumb' + '.' + \
                                     _form.path.data.filename.split('.')[1]
            second_cup_file_name = name_trans + '_second_cup' + '.' + \
                                   _form.path.data.filename.split('.')[1]
            th_second_cup_file_name = name_trans + '_second_cup_thumb' + '.' + \
                                      _form.path.data.filename.split('.')[1]
            first_cup_path = 'application/static/' + first_cup_file_name
            th_first_cup_path = 'application/static/' + th_first_cup_file_name
            second_cup_path = 'application/static/' + second_cup_file_name
            th_second_cup_path = 'application/static/' + th_second_cup_file_name
            print(type(_form.path.data.stream._file))
            _form.path.data.stream._file = io.BytesIO(
                cv2.imencode('.' + _form.path.data.filename.split('.')[1], img_box)[1].tobytes())
            diffusion = len(result['Diffuse'])
            mixed = len(result['Mixed'])
            dense = len(result['Dense'])
            total = diffusion + mixed + dense
            print(total)
            regen_p = (total / 2) / 1.5
            diffusion_percentage = (diffusion / total) * 100
            mixed_percentage = (mixed / total) * 100
            dense_percentage = (dense / total) * 100
            proliferation = (diffusion_percentage + 2 *
                             mixed_percentage + 3 * dense_percentage) / 100
            dsize = (100, 100)
            thfc = cv2.resize(first_cup_g, dsize, interpolation=cv2.INTER_AREA)
            thsc = cv2.resize(second_cup_g, dsize, interpolation=cv2.INTER_AREA)
            cv2.imwrite(first_cup_path, first_cup_g)
            cv2.imwrite(th_first_cup_path, thfc)
            cv2.imwrite(second_cup_path, second_cup_g)
            cv2.imwrite(th_second_cup_path, thsc)
            _form.diff_p.data = round(diffusion_percentage, 2)
            _form.mix_p.data = round(mixed_percentage, 2)
            _form.den_p.data = round(dense_percentage, 2)
            _form.prol.data = round(proliferation, 2)
            _form.regen_p.data = round(regen_p, 2)
            _form.second_cup.data = second_cup_file_name
            _form.first_cup.data = first_cup_file_name
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
