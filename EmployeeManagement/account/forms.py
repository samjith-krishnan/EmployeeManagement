from django import forms
from .models import FormFieldSubmission
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DynamicFieldForm(forms.Form):
    label = forms.CharField(max_length=100)
    field_type = forms.ChoiceField(choices=
                                   [('text', 'Text'),
                                    ('number', 'Number'),
                                    ('date', 'Date'), 
                                    ('password', 'Password'),
                                   
                                    ])

class DynamicfieldValue(forms.ModelForm):
        class Meta:
            model = FormFieldSubmission
            fields = ['field_value']

class UserForm(UserCreationForm):
    
    class Meta:
        model=User
        fields=['username','password1','password2','email']


class LoginForm(forms.Form):

    username = forms.CharField(max_length=100,widget=forms.TextInput(attrs={"class":"login-form"}))
    password = forms.CharField(max_length=100,widget=forms.PasswordInput(attrs={"id":"password"}))


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_new_password = cleaned_data.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise forms.ValidationError("New password and confirmation password do not match.")
        return cleaned_data