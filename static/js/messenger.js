document.addEventListener('DOMContentLoaded', (event) => {
    const chatContainer = document.getElementById('chat-container');
    if (!chatContainer) {
        console.error("Chat container not found!");
        return;
    }

    const interlocutorId = chatContainer.dataset.interlocutorId;
    const currentUserId = parseInt(chatContainer.dataset.userId, 10);
    const wsUrlBase = chatContainer.dataset.wsUrlBase;

    if (!interlocutorId || isNaN(currentUserId) || !wsUrlBase) {
         console.error("Missing or invalid data attributes on chat container!");
         return;
    }

    const wsUrl = wsUrlBase + interlocutorId + '/';
    console.log("Connecting to WebSocket:", wsUrl);

    const chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = function(e) {
        console.log('WebSocket подключен!');
    };

    chatSocket.onmessage = function(e) {
        let data;
        try {
            data = JSON.parse(e.data);
            console.log("Message received:", data); // Отладка полученных данных
        } catch (error) {
             console.error("Error parsing message data:", e.data, error);
             return;
        }

        const messagesDiv = document.getElementById('messages');
        if (!messagesDiv) {
             console.error("Messages div not found!");
             return;
        }

        const messageDiv = document.createElement('div');
        // Сравниваем data.sender_id (число) с currentUserId (число) для определения класса
        const senderId = parseInt(data.sender_id, 10);
        messageDiv.className = `message ${senderId === currentUserId ? 'sent' : 'received'}`;

        // Форматируем время
        let messageTime = '';
        try {
            if (data.timestamp) {
                 messageTime = new Date(data.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            } else {
                 console.warn("Timestamp missing in received message data:", data);
                 messageTime = 'N/A';
            }
        } catch (error) {
             console.error("Error parsing timestamp:", data.timestamp, error);
             messageTime = 'Error';
        }

        const senderName = data.sender_name || 'Неизвестный отправитель'; // Получаем имя отправителя
        const messageContent = data.message || 'Пустое сообщение'; // Получаем текст сообщения

        messageDiv.innerHTML = `
            <div class="message-header"><strong>${senderName}:</strong></div>
            <div class="message-content">${messageContent}</div>
            <div class="message-time">${messageTime}</div>
        `; // <-- Измененная структура HTML

        messagesDiv.appendChild(messageDiv);

        // Прокрутка вниз
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    //остальные обработчики onclose, onerror и логика отправки сообщения

    const messageForm = document.querySelector('#message-form');
    const messageInput = document.querySelector('#message-input');

    if(messageForm && messageInput) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = messageInput.value.trim();

            if (message && chatSocket.readyState === WebSocket.OPEN) {
                try {
                    // Отправляем только текст сообщения, сервер добавит остальное
                    chatSocket.send(JSON.stringify({
                        'message': message,
                    }));
                    messageInput.value = '';
                } catch (sendError) {
                     console.error("Error sending message:", sendError);
                }
            } else if (!message) {
                 console.warn("Attempted to send empty message.");
            } else {
                console.error("WebSocket not open. Current state:", chatSocket.readyState);
            }
        });
    } else {
         console.error("Message form or input not found!");
    }

});