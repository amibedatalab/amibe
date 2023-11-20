from django import forms
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import ReCaptchaField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError  # Import ValidationError
import re # Import regular expressions module
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()
# def validate_chsbc_email(value):
#         if not re.search(r'@canarahsbclife\.in$', value):
#             raise ValidationError(_(settings.INVALID_EMAIL_FIELD_ERROR))

class CustomAuthenticationForm(AuthenticationForm):

    username = forms.EmailField(
        widget=forms.TextInput(attrs={'autofocus': True}),
        # validators=[validate_chsbc_email]  # Add the custom validator
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    # captcha = ReCaptchaField(error_messages={
    #     "required": settings.INVALID_CAPTCHA_ERROR
    # })

    def clean(self):
        email = self.cleaned_data.get('username')  # Use 'username' for email input
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)  # Query by email
            except User.DoesNotExist:
                raise forms.ValidationError(settings.INVALID_FIELD_ERROR)

            if not user.check_password(password):
                raise forms.ValidationError(settings.INVALID_FIELD_ERRORS)

        return self.cleaned_data

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name')
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # if not email.endswith('@canarahsbclife.in'):
        #     raise ValidationError('Email must end with @canarahsbclife.in')
        return email
