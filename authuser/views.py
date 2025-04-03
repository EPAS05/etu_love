from django.shortcuts import render, redirect
from .forms import RegistrationForm, LoginForm, ChangePasswordForm, EditMainProfileForm, EditExtraProfileForm
from .models import User, Profile, ProfilePhoto

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

def settings_page(request):
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
                return redirect('setting_page')
            else:
                password_form.add_error('current_password', 'Неверный пароль')
    return render(request, 'settings.html', { 'user': user, 'profile': profile, 'password_form': password_form })

def edit_main_profile(request):
    user = User.objects.get(id=request.session['user_id'])
    prof = Profile.objects.get(user=user)

    if request.method == "POST":
        form = EditMainProfileForm(request.POST, request.FILES, instance=prof, user=user)
        if form.is_valid():
            form.save(user)
            return redirect('profile')
    else:
        form = EditMainProfileForm(instance=prof, user=user)

    return render(request, 'edit_profile_main.html', {'user': user ,'form': form})


def edit_extra_profile(request):
    if not request.user.is_authenticated:
        return redirect('index')

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('index')

    if request.method == "POST":
        form = EditExtraProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = EditExtraProfileForm(instance=profile)

    return render(request, 'edit_profile_extra.html', {
        'form': form,
        'profile': profile
    })


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