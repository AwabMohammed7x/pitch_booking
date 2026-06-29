from django.contrib.auth.forms import UserCreationForm ,PasswordChangeForm
from django.contrib.auth.models import User
from django import forms
from accounts.models import *
class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'password1', 'password2']:
            
            self.fields[fieldname].widget.attrs['style'] = "width: 100%; padding: 8px;"

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'style': 'width: 100%; padding: 8px;'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'style': 'width: 100%; padding: 8px;'}))

class UserPasswordChange(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['old_password','new_password1','new_password2']:
            self.fields[fieldname].widget.attrs['style'] = "width: 100%; padding: 8px;"


class UserupdateForm(forms.ModelForm):
    
    class Meta:
        model=User
        fields =['username','email']


class ProfileForm(forms.ModelForm):
    
    class Meta:
        model=Profile
        fields =['bio', 'phone_number', 'profile_pic']

        



    