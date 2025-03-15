from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm
from .models import User
from django.contrib.auth.decorators import login_required

def index_page(request):
    reg_form = RegistrationForm()
    login_form = LoginForm()

    if 'register' in request.POST:
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            user = User(
                full_name=reg_form.cleaned_data['full_name'],
                email=reg_form.cleaned_data['email']
            )
            user.set_password(reg_form.cleaned_data['password'])
            user.save()
            request.session['user_id'] = user.id
            return redirect('profile')

    elif 'login' in request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            try:
                user = User.objects.get(email=login_form.cleaned_data['email'])
                if user.check_password(login_form.cleaned_data['password']):
                    request.session['user_id'] = user.id
                    return redirect('profile')
                login_form.add_error('password', 'Неверный пароль')
            except User.DoesNotExist:
                login_form.add_error('email', 'Пользователь не найден')

    return render(request, 'index.html', {
        'reg_form': reg_form,
        'login_form': login_form
    })

def profile(request):
    user = request.user
    if not request.session.get('user_id'):
        return redirect('index_page')
    return render(request, 'profile.html', {'user': user})

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('index_page')

