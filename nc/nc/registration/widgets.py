from turbogears import widgets, validators, identity
from nc.registration import model as register_model

class FakeInputWidget(widgets.Widget):
    "Simple widget that allows displaying its value in a span."
    
    params = ["field_class", "css_classes", "attrs", "has_hidden_field"]
    params_doc = {'field_class' : 'CSS class for the field',
                'attrs' : 'Dictionary containing extra (X)HTML attributes for'
                                    ' the label'
                }
    field_class = None
    attrs = {}
    
    def __init__(self, name=None, label=None, **kw):
        super(FakeInputWidget, self).__init__(name, **kw)
        self.label = label
        self.validator = None
        self.help_text = None
        
    template = """
        <span xmlns:py="http://purl.org/kid/ns#" 
            class="${field_class}" 
            py:content="value" 
            py:attrs="attrs" />
        """

class NewUserFields(widgets.WidgetsList):
    
    user_name = widgets.TextField('user_name',
                    label=_("User Name"),
                    help_text=_("A short name that you will use to log in."))
                    
    email = widgets.TextField('email',
                    label=_("Email"),
                    help_text=_("Your email address (this will be validated)."))
                    
    email_2 = widgets.TextField('email2',
                    label=_("Email (again)"),
                    help_text=_("Your email address again, please."))
    
    display_name = widgets.TextField('display_name',
                    label=_("Display Name"),
                    help_text=_("A longer user name that others will see."))
                    
    password_1 = widgets.PasswordField('password1',
                    label=_("Password"),
                    help_text=_("Your password."))
                    
    password_2 = widgets.PasswordField('password2',
                    label= _("Password (again)"),
                    help_text=_("Same password as above (the two should match)."))
                    
class ExistingUserFields(widgets.WidgetsList):
    
    user_name = FakeInputWidget('user_name',
                    label=_("User Name") )
                    
    email = widgets.TextField('email',
                    label=_("Email"),
                    help_text=_("Your email address (this will be validated)."))
    
    # display_name = widgets.TextField('display_name',
    #                 label=_("Display Name"),
    #                 help_text=_("A longer user name that others will see."))
    
    old_password = widgets.PasswordField('old_password',
                   label=_("Current password"),
                   help_text=_("The current (old) password."))

    password_1 = widgets.PasswordField('password1',
                    label=_("New Password"),
                    help_text=_("Your new password. (If you would like to change it)."))

    password_2 = widgets.PasswordField('password2',
                    label=_("New Password (again)"),
                    help_text=_("New password again (should match the input above)."))
                    
class ResetPasswordFields(widgets.WidgetsList):
    
    display_user_name = FakeInputWidget('display_user_name',
                    label=_("User Name"))
                    
    password_1 = widgets.PasswordField('password1',
                    label=_("New Password"),
                    help_text=_("Your new password."))

    password_2 = widgets.PasswordField('password2',
                    label=_("New Password (again)"),
                    help_text=_("New password again (should match the input above)."))
                    
    key = widgets.HiddenField('key')
    user_name = widgets.HiddenField('user_name')
    
                    
class UniqueUsername(validators.FancyValidator):
    "Validator to confirm that a given user_name is unique."
    def _(s): return s # http://docs.turbogears.org/1.0/Internationalization#id13
    messages = {'notUnique': _('That user name is already being used.')}
    
    def _to_python(self, value, state):
        if not register_model.user_name_is_unique(value):
            raise validators.Invalid(self.message('notUnique', state), value, state)
        return value

class UniqueEmail(validators.FancyValidator):
    "Validator to confirm a given email address is unique."
    def _(s): return s 
    messages = {'notUnique': _('That email address is registered with an existing user.')}
    
    def _to_python(self, value, state):
        if identity.not_anonymous():
            if value == identity.current.user.email_address:
                # the user isn't trying to change their email address
                # so the value is ok
                return value 
        if not register_model.email_is_unique(value):
            raise validators.Invalid(self.message('notUnique', state), value, state)
        return value
        
class ValidPassword(validators.FancyValidator):
    """Validator to test for validity of password."""
    
    def _(s): return s

    messages = {'invalid': _('The password you supplied is invalid.')}

    def validate_python(self, value, state):
        user = identity.current.user
        if not identity.current_provider.validate_password(user, user.user_name, value):
            raise validators.Invalid(
                self.message('invalid', state), value, state)
        return value
        
class ValidResetKey(validators.FormValidator):
    "Validate that the 'user_name' and 'key' fields match entries in the database."
    def _(s): return s
    messages = {
        'no_match'  : _('Password reset not allowed because of bad credentials.') ,
        'missing'   : _('Reset credentials were not found.')
        }

    validate_partial_form = True
    username_field = 'user_name'
    key_field = 'key'

    def validate_partial(self, field_dict, state):
        for name in (self.username_field, self.key_field):
            if not field_dict.has_key(name):
                return
        self.validate_python(field_dict, state)

    def validate_python(self, field_dict, state):
        has_username_key = field_dict.has_key(self.username_field)
        has_key_key = field_dict.has_key(self.key_field)
        if (not has_username_key or not has_key_key):  
            raise validators.Invalid(self.message('missing', state), 
                        field_dict, state)
        user_name = field_dict[self.username_field]
        key = field_dict[self.key_field]
        RegistrationUserLostPassword = register_model.RegistrationUserLostPassword
        ru_lost_pwd = RegistrationUserLostPassword.get_by_username_key(user_name, key)
        if not ru_lost_pwd:
            raise validators.Invalid(self.message('no_match', state), 
                                        field_dict, state)
        
        
class NewUserSchema(validators.Schema):    
    user_name = validators.All(validators.UnicodeString(not_empty=True, 
                                                        max=16, strip=True),
                                UniqueUsername())
    email = validators.All(validators.Email(not_empty=True, max=255),
                                UniqueEmail())
    email2 = validators.All(validators.Email(not_empty=True, max=255))
    display_name = validators.UnicodeString(not_empty=True, strip=True, max=255)
    password1 = validators.UnicodeString(not_empty=True, max=40)
    password2 = validators.UnicodeString(not_empty=True, max=40)
    chained_validators = [validators.FieldsMatch('password1', 'password2'),
                            validators.FieldsMatch('email', 'email2')]
    
class ExistingUserSchema(validators.Schema):
    email = validators.All(validators.Email(not_empty=True, max=255),
                                UniqueEmail())
    old_password = validators.All(validators.UnicodeString(max=40),
                                    ValidPassword())
    password1 = validators.UnicodeString(max=40)
    password2 = validators.UnicodeString(max=40)
    chained_validators = [validators.FieldsMatch('password1', 'password2')]
    
                
class ResetPasswordSchema(validators.Schema):
    password1 = validators.UnicodeString(max=40, not_empty=True)
    password2 = validators.UnicodeString(max=40, not_empty=True)
    user_name = validators.UnicodeString(not_empty=True)
    key = validators.UnicodeString(not_empty=True)
    
    chained_validators = [validators.FieldsMatch('password1', 'password2'),
                        ValidResetKey()]
    
class RegTableForm(widgets.TableForm):
    template = 'nc.templates.registration.tabletemplate'
    
lost_password_form = RegTableForm( fields = [
                                            widgets.TextField('email_or_username',
                                            label=_('User Name or Email Address'),
                                            validator=validators.UnicodeString(not_empty=True, max=255)) ]
                                        )
                                        
delete_user_form = RegTableForm(fields=[
                                    widgets.PasswordField(name='password', 
                                        label=_('Password'),
                                        validator=ValidPassword()),
                                        ],
                                submit=widgets.SubmitButton(attrs=dict(onclick='return confirmDelete();'))
                                )
                                

            
