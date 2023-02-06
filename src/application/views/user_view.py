# Create customized model view class
from application.views.base_view import MyModelView
from wtforms import PasswordField
from flask_security.utils import encrypt_password



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
    
    def add_encrypt(self, _form):
      _form.password.data = encrypt_password(_form.password.data)
      return _form
    
    def create_form(self, obj=None):
       return self.add_encrypt(
          super(UserView, self).create_form(obj)
      )
