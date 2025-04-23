from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, LoginForm, ChangePasswordForm, EditMainProfileForm, EditExtraProfileForm
from .models import User, Profile, ProfilePhoto, get_zodiac_sign, Zodiac
from compatibility.models import  Review
from django.db.models import Avg
from django.core.exceptions import PermissionDenied
from django.contrib import messages

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

            user.profile.birth_date = reg_form.cleaned_data['birth_date']
            user.profile.gender = reg_form.cleaned_data['gender']
            user.profile.zodiac_sign = Zodiac.objects.get(name=get_zodiac_sign(user.profile.birth_date))
            user.profile.save()

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

    reviews = Review.objects.filter(receiver=user).select_related('author__profile')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    context = {
        'user': user,
        'profile': profile,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }

    return render(request, 'profile.html', context)

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('index_page')

def delete_photo(request, photo_uuid):
    if not request.user.is_authenticated:
        return redirect('index_page')
    user = User.objects.get(id=request.session['user_id'])
    profile = user.profile
    photo = get_object_or_404(ProfilePhoto, uuid=photo_uuid)

    if photo.profile != profile:
        raise PermissionDenied

    photo.delete()
    messages.success(request, "Фото успешно удалено.")
    return redirect('profile')


def settings_page(request):
    if not request.user.is_authenticated:
        return redirect('index_page')

    try:
        user = User.objects.get(id=request.session['user_id'])
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('index_page')

    password_form = ChangePasswordForm()
    main_form = EditMainProfileForm(instance=profile, user=user)
    extra_form = EditExtraProfileForm(instance=profile)

    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']
                if user.check_password(current_password):
                    user.set_password(new_password)
                    user.save()
                    request.session['user_id'] = user.id
                    return redirect('settings_page')
                else:
                    password_form.add_error('current_password', 'Неверный пароль')

        elif 'edit_main_profile' in request.POST:
            main_form = EditMainProfileForm(request.POST, request.FILES, instance=profile, user=user)
            if main_form.is_valid():
                main_form.save(user)
                return redirect('settings_page')

        elif 'edit_extra_profile' in request.POST:
            extra_form = EditExtraProfileForm(request.POST, request.FILES, instance=profile)
            if extra_form.is_valid():
                extra_form.save()
                return redirect('settings_page')

    return render(request, 'settings.html', {
        'user': user,
        'profile': profile,
        'password_form': password_form,
        'main_form': main_form,
        'extra_form': extra_form
    })

def friends(request):
    user = request.user
    if not request.session.get('user_id'):
        return redirect('index_page')
    return render(request, 'friends.html')

def messages_page(request):
    user = request.user
    if not request.session.get('user_id'):
        return redirect('index_page')
    return render(request, 'messages.html')