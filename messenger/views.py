from django.contrib.auth.decorators import login_required
from authuser.models import User
from compatibility.models import Friendship
from django.shortcuts import render, get_object_or_404
from messenger.models import Message
from django.db.models import Q, Max
from django.http import HttpResponseForbidden
from django.utils import timezone


def messenger(request): #Лист диалогов
    current_user = request.user
    sent_to_user_ids = Message.objects.filter(receiver=current_user).values_list('sender_id', flat=True) #айди пользователей, кто отправлял нам сообщение
    sent_by_user_ids = Message.objects.filter(sender=current_user).values_list('receiver_id', flat=True) #Кому мы

    interlocutor_ids = set(list(sent_by_user_ids) + list(sent_to_user_ids)) #Список уникальных айди пользователей

    try:
        ai_user = User.objects.get(id=11) #Обработка нейропользователя
        interlocutor_ids.add(ai_user.id) #Добавляем в собеседники
    except User.DoesNotExist:
        print("No ai")

    interlocutors = User.objects.filter(id__in=interlocutor_ids) #Уникальные собеседники

    dialogs_data = [] #Диалоги

    for interlocutor in interlocutors:
        last_message = Message.objects.filter( #Получаем последнее сообщение
            (Q(sender=current_user,
               receiver=interlocutor) |
             Q(sender=interlocutor, receiver=current_user))
        ).order_by('-timestamp').first()
        if last_message or (hasattr(interlocutor, 'is_ai') and interlocutor.is_ai):
            dialog_info = { #Собеседник + последнее сообщение
                'interlocutor': interlocutor,
                'last_message': last_message
            }

            if (hasattr(interlocutor, 'is_ai') and interlocutor.is_ai) and not last_message: #Если ии и нет сообщений
                dialog_info['last_message'] = type('obj', (object,), {
                    'text': "Начать диалог с нейросетью",
                    'timestamp': timezone.now()
                })()
            dialogs_data.append(dialog_info)

    dialogs_data.sort(key=lambda x: x['last_message'].timestamp, reverse=True) #Сортируем по времени

    context = {
        'dialogs': dialogs_data,
        'user': current_user,
    }

    return render(request, 'dialog_list.html', context)

@login_required
def messenger_detail(request, user_id): #Диалог с пользователем
    user = request.user
    interlocutor = get_object_or_404(User, id=user_id) #Собеседник

    try:
        if not Friendship.objects.filter and not interlocutor.is_ai( #Проверка мэтча - не мэтчи не могу общаться
                (Q(from_user=user, to_user=interlocutor) |
                 Q(from_user=interlocutor, to_user=user)),
                status='accepted'
        ).exists():
            return HttpResponseForbidden("Ошибка доступа: Пользователи не являются друзьями")
    except Exception as e:
        print(f"Error checking friendship: {e}")
        return HttpResponseForbidden("Ошибка доступа при проверке дружбы")

    messages = Message.objects.filter(  #Получение списка сообщений
        Q(sender=user, receiver=interlocutor) |
        Q(sender=interlocutor, receiver=user)
    ).order_by('timestamp')

    host_with_port = request.get_host() #Получаем адрес
    host = host_with_port.split(':')[0]
    websocket_port = 8001 #Меняем порт
    websocket_url_base = f"ws://{host}:{websocket_port}/ws/messenger" #Для django-channels - асинхронной отправки сообщений

    context = {
        'interlocutor': interlocutor,
        'messages': messages,
        'interlocutor_id': interlocutor.id,
        'user_id': user.id,
        'ws_url_base': websocket_url_base
    }

    return render(request, 'messenger_detail.html', context)