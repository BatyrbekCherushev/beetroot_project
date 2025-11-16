from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, CustomLoginForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView

#========================================================================================= REGISTER PAGE =====================================================================================
def register_user(request):

    register_form = CustomUserCreationForm()

    if request.method == 'POST':
        if 'register_submit' in request.POST:
            register_form = CustomUserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                login(request, user)
                return redirect('app_site:profile')
    return render(request, 'app_authentification/register.html', {
        'app_name': 'app_authentification',
        'register_form': register_form,
        'page_name': 'register',
        'page_name_title': 'Створення нового користувача'})


def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('app_site:profile') 
    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next') or 'app_site:profile'
                return redirect(next_url)

    return render(request, 'app_authentification/login.html', {
        'form': form,
        'app_name': 'app_authentification',
        'page_name': 'login',
        'page_name_title': 'Авторизація'
    })
    