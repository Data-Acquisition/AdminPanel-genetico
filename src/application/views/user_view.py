# Create customized model view class
from application.views.base_view import MyModelView
from wtforms import PasswordField


class UserView(MyModelView):
    list_template = "admin/model/list.html"
    column_searchable_list = ['email', 'first_name', 'last_name']
    column_exclude_list = ['password']
    # form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = ['email', 'first_name', 'last_name']
    form_overrides = {
        'password': PasswordField
    }
