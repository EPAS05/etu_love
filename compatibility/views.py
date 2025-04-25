from django.contrib.auth.decorators import login_required

from authuser.models import User, Profile, Gender
from compatibility.forms import SelectedCriterionForm, ComparisonSettingsForm, PairsCriteriaForm, ReviewForm
from compatibility.models import SelectedCriterion, ComparisonSettings, PairsCriteria, Friendship, Review
from compatibility.services.ahp import AHPCalc
from compatibility.services.matcher import MatcherCalc
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Avg
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from itertools import combinations

@login_required
def search_settings(request):
    user = request.user

    selected_criterion, _ = SelectedCriterion.objects.get_or_create(user=user)
    comparison_settings, _ = ComparisonSettings.objects.get_or_create(user=user)

    criteria_form = SelectedCriterionForm(instance=selected_criterion)
    values_form = None
    show_values_form = False
    matches = []

    if request.method == 'POST':
        if 'criteria_submit' in request.POST:
            criteria_form = SelectedCriterionForm(request.POST, instance=selected_criterion)
            if criteria_form.is_valid():
                criteria_form.save()
                show_values_form = criteria_form.instance.criteria.exists()
                return redirect('search_settings')

        elif 'values_submit' in request.POST:
            values_form = ComparisonSettingsForm(
                request.POST,
                instance=comparison_settings,
                user=user
            )
            if values_form.is_valid():
                values_form.save()
                return redirect('search_settings')

        elif 'refresh_matches' in request.POST:
            pass

    if not criteria_form:
        criteria_form = SelectedCriterionForm(instance=selected_criterion)

    if selected_criterion.criteria.exists():
        if not values_form:
            values_form = ComparisonSettingsForm(
                instance=comparison_settings,
                user=user
            )
        show_values_form = True
        AHPCalc.find_weights(user)
        raw_matches = []
        if user.profile.relationship.name == 'Партнера':
            opposite_gender = 'Мужской' if user.profile.gender.name == 'Женский' else 'Женский'
            gender_obj = Gender.objects.get(name=opposite_gender)

            profiles = Profile.objects.filter(gender=gender_obj.id, relationship=user.profile.relationship).exclude(user=user)

        elif user.profile.relationship.name == 'Общение':
            profiles = Profile.objects.filter(relationship=user.profile.relationship).exclude(user=user)

        for profile in profiles:
            score = MatcherCalc.find_compability(user, profile)
            raw_matches.append({
                'profile': profile,
                'score': score
            })

        matches = sorted(raw_matches, key=lambda x: x['score'], reverse=True)[:10]

    return render(request, 'search.html', {
        'criteria_form': criteria_form,
        'values_form': values_form if show_values_form else None,
        'show_values_section': show_values_form,
        'user': user,
        'matches': matches,
    })

@login_required
def compare_criteria(request):
    user = request.user
    selected_criterion = SelectedCriterion.objects.get(user=user)
    criteria = selected_criterion.criteria.all()

    for a, b in combinations(criteria, 2):
        if a.id > b.id:
            a, b = b, a
        PairsCriteria.objects.get_or_create(
            user=user,
            criterion_a=a,
            criterion_b=b,
            defaults={'score': 3}
        )

    comparisons = PairsCriteria.objects.filter(
        user=user,
        criterion_a__in=criteria,
        criterion_b__in=criteria
    ).order_by('criterion_a', 'criterion_b')

    FormSet = modelformset_factory(
        PairsCriteria,
        form=PairsCriteriaForm,
        extra=0
    )

    if request.method == 'POST':
        formset = FormSet(request.POST, queryset=comparisons)
        if formset.is_valid():
            formset.save()
            return redirect('search_settings')
    else:
        formset = FormSet(queryset=comparisons)

    comparisons_data = []
    for form, comp in zip(formset.forms, comparisons):
        comparisons_data.append({
            'form': form,
            'criterion_a': comp.criterion_a,
            'criterion_b': comp.criterion_b,
        })

    return render(request, 'compare.html', {
        'formset': formset,
        'comparisons_data': comparisons_data,
    })

@login_required
def user_profile(request, user_id):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    if request.user.id == user_id:
        return redirect('profile')

    can_review = False
    if request.user.is_authenticated and request.user != user:
        can_review = not Review.objects.filter(author=request.user, receiver=user).exists()

    reviews = Review.objects.filter(receiver=user).select_related('author__profile')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    if request.method == 'POST' and 'submit_review' in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid() and can_review:
            review = form.save(commit=False)
            review.author = request.user
            review.receiver = user
            review.save()
            return redirect('user_profile', user_id=user_id)
    else:
        form = ReviewForm()

    context = {
        'profile': profile,
        'user': user,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_form': form,
        'can_review': can_review,
    }
    return render(request, 'user_profile.html', context)

@login_required
def friends(request):
    incoming_requests = Friendship.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user')

    outgoing_requests = Friendship.objects.filter(
        from_user=request.user,
        status='pending'
    ).select_related('to_user')

    friends = Friendship.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).select_related('from_user', 'to_user')

    context = {
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
        'friends': friends,
    }
    return render(request, 'friends.html', context)


def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, pk=user_id)

    if request.user == to_user:
        messages.error(request, "Нельзя отправить заявку самому себе")
        return redirect('user_profile', user_id=user_id)

    if Friendship.objects.filter(from_user=request.user, to_user=to_user).exists():
        messages.warning(request, "Заявка уже отправлена")
        return redirect('user_profile', user_id=user_id)

    Friendship.objects.create(from_user=request.user, to_user=to_user)
    messages.success(request, "Заявка успешно отправлена")
    return redirect('user_profile', user_id=user_id)

def cancel_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id)

    if friendship.from_user != request.user:
        raise PermissionDenied("Вы не можете отменить эту заявку")

    friendship.delete()
    messages.info(request, "Заявка отменена")
    return redirect('friends')

def accept_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id)

    if friendship.to_user != request.user:
        raise PermissionDenied("Вы не можете принять эту заявку")

    friendship.status = 'accepted'
    friendship.save()
    messages.success(request, "Заявка принята")
    return redirect('friends')

def decline_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, pk=friendship_id)

    if friendship.to_user != request.user:
        raise PermissionDenied("Вы не можете отклонить эту заявку")

    friendship.status = 'declined'
    friendship.save()
    messages.info(request, "Заявка отклонена")
    return redirect('friends')


def remove_friend(request, friend_id):
    friend = get_object_or_404(User, pk=friend_id)

    friendship = Friendship.objects.filter(
        Q(from_user=request.user, to_user=friend) |
        Q(from_user=friend, to_user=request.user),
        status='accepted'
    ).first()

    if not friendship:
        messages.error(request, "Этот пользователь не является вашим другом")
        return redirect('friends')

    friendship.delete()
    messages.success(request, "Пользователь удален из друзей")
    return redirect('friends')




