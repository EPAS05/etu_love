from django.contrib.auth.decorators import login_required
from authuser.models import User
from django.shortcuts import render, get_object_or_404
from messenger.models import Message
from django.db.models import Q, Max
from django.http import HttpResponseForbidden
from django.utils import timezone


def messenger(request):
    current_user = request.user
    sent_to_user_ids = Message.objects.filter(receiver=current_user).values_list('sender_id', flat=True)
    sent_by_user_ids = Message.objects.filter(sender=current_user).values_list('receiver_id', flat=True)

    interlocutor_ids = set(list(sent_by_user_ids) + list(sent_to_user_ids))

    try:
        ai_user = User.objects.get(id=11)
        interlocutor_ids.add(ai_user.id)
    except User.DoesNotExist:
        print("Dialog list: AI user not found in database.")

    interlocutors = User.objects.filter(id__in=interlocutor_ids)

    dialogs_data = []

    for interlocutor in interlocutors:
        last_message = Message.objects.filter(
            (Q(sender=current_user,
               receiver=interlocutor) |
             Q(sender=interlocutor, receiver=current_user))
        ).order_by('-timestamp').first()
        if last_message or (hasattr(interlocutor, 'is_ai') and interlocutor.is_ai):
            dialog_info = {
                'interlocutor': interlocutor,
                'last_message': last_message
            }

            if (hasattr(interlocutor, 'is_ai') and interlocutor.is_ai) and not last_message:
                dialog_info['last_message'] = type('obj', (object,), {
                    'text': "Начать диалог с нейросетью",
                    'timestamp': timezone.now()
                })()
            dialogs_data.append(dialog_info)

    dialogs_data.sort(key=lambda x: x['last_message'].timestamp, reverse=True)

    context = {
        'dialogs': dialogs_data,
        'user': current_user,
    }

    return render(request, 'dialog_list.html', context)

@login_required
def messenger_detail(request, user_id):
    user = request.user # Аутентифицированный пользователь из декоратора @login_required
    interlocutor = get_object_or_404(User, id=user_id)

    try:
        from compatibility.models import Friendship # <-- Возможно, нужно импортировать здесь или вверху
        if not Friendship.objects.filter(
                (Q(from_user=user, to_user=interlocutor) |
                 Q(from_user=interlocutor, to_user=user)),
                status='accepted' # Предполагается поле status
        ).exists():
            # Если не друзья, возвращаем ошибку доступа
            return HttpResponseForbidden("Ошибка доступа: Пользователи не являются друзьями")
    except Exception as e:
        # Обработка случая, если модель Friendship не найдена или другая ошибка
        print(f"Error checking friendship: {e}")
        # Возможно, стоит запретить доступ или показать ошибку
        return HttpResponseForbidden("Ошибка доступа при проверке дружбы")


    # --- Получение или создание тестового сообщения ---
    # Этот блок создания тестового сообщения выполняется при каждом заходе, если сообщений нет.
    # Возможно, стоит выполнять его только один раз при первом открытии диалога.
    messages = Message.objects.filter(
        Q(sender=user, receiver=interlocutor) |
        Q(sender=interlocutor, receiver=user)
    ).order_by('timestamp')

    """if messages.count() == 0:
        try:
            Message.objects.create(
                sender=user,
                receiver=interlocutor,
                text="Тестовое сообщение"
            )
            # Перезапрашиваем сообщения после создания
            messages = Message.objects.filter(
                Q(sender=user, receiver=interlocutor) |
                Q(sender=interlocutor, receiver=user)
            ).order_by('timestamp')
            print(f"Debug: Created a test message.") # Отладочный вывод
        except Exception as e:
             print(f"Error creating test message: {e}")"""


    print(f"Debug: Found {messages.count()} messages")  # Отладочный вывод

    # --- Вычисляем хост и порт для WebSocket ---
    # Получаем хост из request.get_host() (например, '127.0.0.1:8000')
    host_with_port = request.get_host()
    # Разбиваем на хост и порт, берем только хост
    # Если host_with_port содержит порт, берем часть до двоеточия
    host = host_with_port.split(':')[0]
    # Явно указываем порт для WebSocket
    websocket_port = 8001
    # Формируем базовый URL для WebSocket без конечного слэша
    websocket_url_base = f"ws://{host}:{websocket_port}/ws/messenger" # Не добавляем конечный слэш здесь

    context = {
        'interlocutor': interlocutor,
        'messages': messages,
        'interlocutor_id': interlocutor.id, # Передаем ID собеседника
        'user_id': user.id, # Передаем ID текущего пользователя
        'ws_url_base': websocket_url_base # <-- Передаем вычисленный URL в контекст
    }

    return render(request, 'messenger_detail.html', context)