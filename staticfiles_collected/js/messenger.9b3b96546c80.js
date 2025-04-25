document.addEventListener('DOMContentLoaded', (event) => {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) {
        console.error("Chat container not found!");
        // Важно выйти, если контейнер не найден
        return;
    }

    const interlocutorId = chatContainer.dataset.interlocutorId;
    // Преобразуем в число сразу при получении
    const currentUserId = parseInt(chatContainer.dataset.userId, 10);
    // Получаем базовый URL
    const wsUrlBase = chatContainer.dataset.wsUrlBase;

    // Улучшенная проверка на наличие всех необходимых данных
    if (!interlocutorId || isNaN(currentUserId) || !wsUrlBase) {
         console.error("Missing or invalid data attributes on chat container!");
         return;
    }

    // Формируем полный URL для WebSocket
    const wsUrl = wsUrlBase + interlocutorId + '/';
    console.log("Connecting to WebSocket:", wsUrl); // Отладка URL

    const chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = function(e) {
        console.log('WebSocket подключен!');
        // Здесь можно отправить первое сообщение, если это необходимо для аутентификации
        // или инициализации на сервере
    };

    chatSocket.onmessage = function(e) {
        let data;
        try {
            data = JSON.parse(e.data);
            console.log("Message received:", data); // Отладка полученных данных
        } catch (error) {
             console.error("Error parsing message data:", e.data, error);
             return; // Прерываем обработку, если данные невалидны
        }


        const messagesDiv = document.getElementById('messages');
        if (!messagesDiv) {
             console.error("Messages div not found!");
             return;
        }

        const messageDiv = document.createElement('div');
        // Сравниваем data.sender_id с currentUserId
        // Убедитесь, что data.sender_id приходит с сервера как число,
        // иначе может потребоваться parseInt(data.sender_id, 10) для сравнения
        messageDiv.className = `message ${data.sender_id === currentUserId ? 'sent' : 'received'}`;

        // Форматируем время
        let messageTime = ''; // Изначально пустая строка на случай ошибки
        try {
            // Проверяем, что timestamp существует и не пустой
            if (data.timestamp) {
                 // Используем toLocaleTimeString для более гибкого форматирования времени
                 messageTime = new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } else {
                 console.warn("Timestamp missing in received message data:", data);
                 messageTime = 'N/A'; // Или другое обозначение отсутствия времени
            }
        } catch (error) {
             console.error("Error parsing timestamp:", data.timestamp, error);
             messageTime = 'Error'; // Обозначение ошибки парсинга
        }

        // Убедитесь, что у вас есть поле 'message' в данных от сервера
        const messageContent = data.message || 'Пустое сообщение'; // Защита от отсутствия поля 'message'

        messageDiv.innerHTML = `
            <div class="message-content">${messageContent}</div>
            <div class="message-time">${messageTime}</div>
        `;
        messagesDiv.appendChild(messageDiv);

        // Прокрутка вниз после добавления сообщения
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    chatSocket.onclose = function(e) {
        console.error('WebSocket отключен! Код:', e.code, 'Причина:', e.reason, 'Was Clean:', e.wasClean);
        // Здесь можно добавить логику переподключения
        // Например, setTimeout(() => connectWebSocket(), 5000);
    };

    chatSocket.onerror = function(error) {
         console.error('WebSocket ошибка:', error);
         // onerror обычно предшествует onclose,
         // так что логика обработки отключения сработает
    }

    const messageForm = document.querySelector('#message-form');
    const messageInput = document.querySelector('#message-input');

    if(messageForm && messageInput) { // Проверяем наличие обоих элементов
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Предотвращаем стандартную отправку формы
            const message = messageInput.value.trim();

            // Проверяем, что сообщение не пустое И сокет открыт
            if (message && chatSocket.readyState === WebSocket.OPEN) {
                try {
                    chatSocket.send(JSON.stringify({
                        'message': message,
                        // Возможно, нужно также отправить sender_id или другую информацию
                        // 'sender_id': currentUserId,
                        // 'recipient_id': interlocutorId // Если логика сервера этого требует
                    }));
                    messageInput.value = ''; // Очищаем поле ввода после успешной отправки
                } catch (sendError) {
                     console.error("Error sending message:", sendError);
                     // Добавить обратную связь пользователю об ошибке отправки
                }
            } else if (!message) {
                 console.warn("Attempted to send empty message.");
                 // Можно показать сообщение пользователю, что нельзя отправлять пустое сообщение
            } else { // сокет не открыт
                console.error("WebSocket not open. Current state:", chatSocket.readyState);
                // Можно уведомить пользователя, что соединение потеряно
            }
        });
    } else {
         console.error("Message form or input not found!");
    }

    // Убираем тестовую отправку, как вы и сделали
});