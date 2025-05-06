from django.contrib.auth.decorators import login_required
from authuser.forms import RegistrationForm, LoginForm, ChangePasswordForm, EditMainProfileForm, EditExtraProfileForm
from authuser.models import User, ProfilePhoto, get_zodiac_sign, Zodiac
from compatibility.models import Review, Friendship
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout


def index_page(request): #Первая страница что видна при заходе на сайт
    reg_form = RegistrationForm()
    login_form = LoginForm()
    reg = False

    if request.user.is_authenticated:  #Проверка зарегестрирован ли (важно для хтмл)
        reg = True

    if 'register' in request.POST: #Обработка регистрации
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            user = User(
                full_name=reg_form.cleaned_data['full_name'],
                email=reg_form.cleaned_data['email']
            )
            user.set_password(reg_form.cleaned_data['password'])
            user.save() #Сохранение пользователя

            user.profile.birth_date = reg_form.cleaned_data['birth_date']
            user.profile.gender = reg_form.cleaned_data['gender']
            user.profile.zodiac_sign = Zodiac.objects.get(name=get_zodiac_sign(user.profile.birth_date))
            user.profile.save() #Его профиля

            authenticated_user = authenticate(request, email=user.email, password=reg_form.cleaned_data['password'])
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('profile') #Заходим в акк
            else:
                pass

    elif 'login' in request.POST:  #Проверки при входе
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                login_form.add_error(None, 'Неверный Email или пароль')

    return render(request, 'index.html', {
        'reg_form': reg_form,
        'login_form': login_form,
        'reg': reg
    })


@login_required
def profile(request): #Сам профиль пользователя
    user = request.user
    profile = user.profile

    reviews = Review.objects.filter(receiver=user).select_related('author__profile') #Отзывы
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0 #Рейтинг

    matches_cnt = User.objects.filter(
        Q(sent_requests__to_user=user, sent_requests__status='accepted') |
        Q(received_requests__from_user=user, received_requests__status='accepted')
    ).distinct().count()  #Количество метчей

    context = {
        'user': user,
        'matches_cnt': matches_cnt,
        'profile': profile,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
    }

    return render(request, 'profile.html', context)


def logout_view(request): #Выход из системы
    logout(request)
    return redirect('index_page')

@login_required
def delete_photo(request, photo_uuid):  #Удаление фото
    user = request.user
    profile = user.profile
    photo = get_object_or_404(ProfilePhoto, uuid=photo_uuid)

    if photo.profile != profile: #Если фото чужое
        raise PermissionDenied

    photo.delete()
    messages.success(request, "Фото успешно удалено.")
    return redirect('profile')

@login_required
def settings_page(request):  #Настройки основные
    user = request.user
    profile = request.user.profile

    password_form = ChangePasswordForm()
    main_form = EditMainProfileForm(instance=profile, user=user)
    extra_form = EditExtraProfileForm(instance=profile)

    if request.method == 'POST':
        if 'change_password' in request.POST:  #Смена пароля
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                current_password = password_form.cleaned_data['current_password']
                new_password = password_form.cleaned_data['new_password']
                if user.check_password(current_password):  #Подтверждение текущего пароля (сравнение новых в валидации формы)
                    user.set_password(new_password)
                    user.save()
                    request.session['user_id'] = user.id
                    return redirect('settings_page')
                else:
                    password_form.add_error('current_password', 'Неверный пароль')

        elif 'edit_main_profile' in request.POST: #Просто основная форма
            main_form = EditMainProfileForm(request.POST, request.FILES, instance=profile, user=user)
            if main_form.is_valid():
                main_form.save(user)
                return redirect('settings_page')

        elif 'edit_extra_profile' in request.POST: #Вторая форма
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
