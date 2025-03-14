from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Prénom')
    last_name = forms.CharField(required=True, label='Nom')
    phone = forms.CharField(required=False, label='Téléphone')
    function = forms.CharField(required=True, label='Fonction')
    company = forms.CharField(required=True, label='Entreprise')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'phone', 'function', 'company', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' 