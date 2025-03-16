from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, ChangePasswordForm
from .models import User

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
    if not request.session.get('user_id'):
        return redirect('index_page')

    try:
        user = User.objects.get(id=request.session['user_id'])
        profile = user.profile
    except User.DoesNotExist:
        return redirect('index_page')

    return render(request, 'profile.html', {'user': user, 'profile': profile})

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('index_page')

def settings(request):
    if not request.session.get('user_id'):
        return redirect('index_page')

    user = User.objects.get(id=request.session['user_id'])
    password_form = ChangePasswordForm()

    if request.method == 'POST' and 'change_password' in request.POST:
        password_form = ChangePasswordForm(request.POST)
        if password_form.is_valid():
            current_password = password_form.cleaned_data['current_password']
            new_password = password_form.cleaned_data['new_password']
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                request.session['user_id'] = user.id
                return redirect('settings')
            else:
                password_form.add_error('current_password', 'Неверный пароль')
    return render(request, 'settings.html', { 'user': user, 'password_form': password_form })


def friends(request):
    user = request.user
    if not request.session.get('user_id'):
        return redirect('index_page')
    return render(request, 'friends.html')

def messages(request):
    user = request.user
    if not request.session.get('user_id'):
        return redirect('index_page')
    return render(request, 'messages.html')