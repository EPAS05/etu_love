from django.contrib.auth.decorators import login_required
from authuser.models import User, Profile, Gender
from authuser.views import settings_page
from compatibility.forms import SelectedCriterionForm, ComparisonSettingsForm, PairsCriteriaForm, ReviewForm
from compatibility.models import SelectedCriterion, ComparisonSettings, PairsCriteria, Friendship, Review, CriterionWeight, Block
from compatibility.services.ahp import AHPCalc
from compatibility.services.matcher import MatcherCalc
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Avg
from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from itertools import combinations
from django.http import HttpResponseForbidden

@login_required
def search_settings(request):
    user = request.user

    if user.profile.relationship is None:
        return redirect(settings_page)

    selected_criterion, _ = SelectedCriterion.objects.get_or_create(user=user)
    comparison_settings, _ = ComparisonSettings.objects.get_or_create(user=user)

    criteria_form = SelectedCriterionForm(instance=selected_criterion)
    values_form = None
    show_values_form = False
    matches = []
    cr = 0

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
        criterion_weight = CriterionWeight.objects.filter(user=user).first()
        cr = round(criterion_weight.consistency_ratio, 2) if criterion_weight else 0
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
        'cr': cr,
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
    if user.id == user_id:
        return redirect('profile')

    user_prof = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user_prof)

    can_review = not Review.objects.filter(author=user, receiver=user_prof).exists()
    reviews = Review.objects.filter(receiver=user_prof).select_related('author__profile')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    friendship = Friendship.objects.filter(
        (Q(from_user=user, to_user=user_prof) | Q(from_user=user_prof, to_user=user)),
        status__in=['pending', 'accepted']
    ).first()

    friendship_status = friendship.status if friendship else 'none'
    friendship_id = friendship.id if friendship else None
    is_request_sent = friendship.from_user == user if friendship else False

    if request.method == 'POST' and 'submit_review' in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid() and can_review:
            review = form.save(commit=False)
            review.author = user
            review.receiver = user_prof
            review.save()
            return redirect('user_profile', user_id=user_id)
    else:
        form = ReviewForm()

    context = {
        'profile': profile,
        'user': user_prof,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1),
        'review_form': form,
        'can_review': can_review,
        'friendship_status': friendship_status,
        'friendship_id': friendship_id,
        'is_request_sent': is_request_sent,
        'is_blocked': Block.objects.filter(blocker=user, blocked=user_prof).exists(),
        'is_blocked_by_user': Block.objects.filter(blocker=user_prof, blocked=user).exists(),
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

    if Block.objects.filter(blocker=request.user, blocked=to_user).exists():
        return HttpResponseForbidden("Вы заблокировали этого пользователя")
    if Block.objects.filter(blocker=to_user, blocked=request.user).exists():
        return HttpResponseForbidden("Пользователь заблокировал вас")

    existing = Friendship.objects.filter(
        (Q(from_user=request.user, to_user=to_user) |
         Q(from_user=to_user, to_user=request.user))
    ).first()

    if existing:
        if existing.status == 'accepted':
            messages.warning(request, "Уже друзья")
        elif existing.from_user == request.user:
            messages.warning(request, "Заявка уже отправлена")
        else:
            existing.status = 'accepted'
            existing.save()
            messages.success(request, "Заявка автоматически принята")
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

    reverse_friendship = Friendship.objects.filter(
        from_user=request.user,
        to_user=friendship.from_user
    ).first()

    if reverse_friendship:
        reverse_friendship.delete()

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


@login_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, pk=user_id)

    if Block.objects.filter(blocker=request.user, blocked=user_to_block).exists():
        return redirect('user_profile', user_id=user_id)

    Block.objects.create(blocker=request.user, blocked=user_to_block)
    return redirect('user_profile', user_id=user_id)


@login_required
def unblock_user(request, user_id):
    user_to_unblock = get_object_or_404(User, pk=user_id)
    Block.objects.filter(blocker=request.user, blocked=user_to_unblock).delete()
    return redirect('user_profile', user_id=user_id)