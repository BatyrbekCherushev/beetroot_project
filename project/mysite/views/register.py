from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

#========================================================================================= REGISTER PAGE =====================================================================================
def register_user(request):
    register_form = UserCreationForm()
    if request.method == 'POST':
        # Якщо форма реєстрації була надіслана
        if 'register_submit' in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                # UserSettings створюється автоматично через сигнал post_save
                login(request, user)
                return redirect('index')  # редірект на головну сторінку
    context = {
        'register_form': register_form
    }
    return render(request, 'register.html', context)