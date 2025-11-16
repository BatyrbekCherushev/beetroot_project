from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Ім’я користувача',
        label_suffix='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            
            'placeholder': 'Введіть ім’я користувача',
            'style': 'width: 300px;',
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введіть пароль',
            'style': 'width: 300px;',
        })
    )

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Електронна пошта',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            # 'style': 'width: 300px;',
            'placeholder': 'Enter your email here...',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Ім`я',
            'password1': 'Пароль',
            'password2': 'Підтвердження пароля',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter user name...'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            # 'style': 'width: 300px;',
            'placeholder': 'Введіть пароль',
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            # 'style': 'width: 300px;',
            'placeholder': 'Повторіть пароль',
        })



