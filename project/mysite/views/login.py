from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
#========================================================================================= LOGIN PAGE =====================================================================================
def login_user(request):
    login_form = AuthenticationForm()
    

    if request.method == 'POST':
        # Якщо форма логіну була надіслана
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('index')

    context = {
        'login_form': login_form,
    }
    return render(request, 'login.html', context)