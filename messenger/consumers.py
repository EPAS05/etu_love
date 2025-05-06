import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from channels.db import database_sync_to_async
from authuser.models import User
from compatibility.models import Friendship
from messenger.models import Message
import shortuuid
import logging

from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

logger = logging.getLogger(__name__)

LOCAL_MODEL_PATH = "ai_models/my_model" #Путь к модели ии пользователя

ai_tokenizer = None #Токенайзер
ai_model = None #ИИ пользователь
AI_DEVICE = "cpu" #Устройство

try:
    logger.info(f"Попытка загрузки T5 модели и токенизатора из {LOCAL_MODEL_PATH}...")

    ai_tokenizer = T5Tokenizer.from_pretrained(LOCAL_MODEL_PATH) #Загрузка токенайзера
    logger.info("Токенизатор загружен.")

    AI_DEVICE = "cuda" if torch.cuda.is_available() else "cpu" #Устройство
    logger.info(f"Устройство: {AI_DEVICE}")

    ai_model = T5ForConditionalGeneration.from_pretrained(LOCAL_MODEL_PATH)
    ai_model.to(AI_DEVICE)
    ai_model.eval()
    logger.info("Модель загружена и перемещена на устройство.")

except Exception as e: #Ошибка
    logger.error(f"ФАТАЛЬНАЯ ОШИБКА: {e}")
    ai_tokenizer = None
    ai_model = None
    AI_DEVICE = "cpu"


async def get_ai_response(message_text, conversation_history, tokenizer, model, device):  #Получение ответа нейросети
    if model is None or tokenizer is None:
        logger.error("Модель или токенизатор не загружены.")
        return "Извините, модель нейросети недоступна."

    logger.info(f"Генерация ответа для: '{message_text}'")

    try:
        #input_parts = []
        #for msg in conversation_history:  #Обрабатываем историю диалога для нейросети
        #    role_prefix = "user: " if msg.sender.is_ai else "bot: "
        #    input_parts.append(f"{role_prefix}{msg.text}")

        #input_parts.append(f"user: {message_text}")
        #input_text = " ".join(input_parts)
        input_text = message_text

        inputs = tokenizer(input_text, return_tensors='pt').to(device)

        with torch.no_grad():
             hypotheses = model.generate(
                 **inputs,
                 temperature=0.9,
                 do_sample=True,
                 top_p=0.7,
                 num_return_sequences=1,
                 repetition_penalty=2.5,
                 max_new_tokens=32,
                 pad_token_id=tokenizer.eos_token_id,
                 eos_token_id=tokenizer.eos_token_id,
             )

        ai_response_text = tokenizer.decode(hypotheses[0], skip_special_tokens=True)  #Создаем ответ

        if ai_response_text.startswith(input_text):
             ai_response_text = ai_response_text[len(input_text):].strip()


        return ai_response_text.strip()

    except Exception as e:
        logger.exception(f"Ошибка при инференсе модели: {e}")
        return "Произошла ошибка при генерации ответа нейросети."

class ChatConsumer(AsyncWebsocketConsumer):  #Обработка чата
    ai_tokenizer = ai_tokenizer
    ai_model = ai_model
    ai_device = AI_DEVICE

    async def connect(self): #Коннект
        self.user = self.scope["user"]
        logger.info(f"WebSocket connect: Attempt. User: {self.user}")
        if not self.user or not self.user.is_authenticated: #Проверка пользователя и аутентификации (если нет, закрываем соединение)
            logger.warning("WebSocket connect: Unauthenticated user attempt. Closing.")
            await self.close()
            return

        try:
            self.interlocutor_id = int(self.scope['url_route']['kwargs']['user_id'])
            self.interlocutor = await self.get_interlocutor_user(self.interlocutor_id) #Получаем собеседника

            if not self.interlocutor:
                 logger.warning(f"WebSocket connect: Interlocutor user {self.interlocutor_id} not found. Closing.")
                 await self.close()
                 return

        except (ValueError, KeyError) as e: #Обработка ошибок
             logger.error(f"WebSocket connect: Error getting interlocutor ID: {e}. Closing.")
             await self.close()
             return
        except User.DoesNotExist:
             logger.warning(f"WebSocket connect: Interlocutor user {self.interlocutor_id} not found (DoesNotExist). Closing.")
             await self.close()
             return


        logger.info(f"WebSocket connect: User '{self.user.email}' (ID: {self.user.id}) attempting connection with User ID: {self.interlocutor_id}")

        is_friend = await self.check_friendship() #Проверка дружбы и ии ли пользователь
        is_interlocutor_ai = hasattr(self.interlocutor, 'is_ai') and self.interlocutor.is_ai
        if not is_friend and not is_interlocutor_ai: #Не друзья и не ии
            logger.warning(f"WebSocket connect: User {self.user.id} и {self.interlocutor_id} не друзья")
            await self.close()
            return

        try:
            user_ids = sorted([str(self.user.id), str(self.interlocutor_id)])  #Сортируем айди пользователей для уникального и одинакового названия комнаты
            room_identifier = "-".join(user_ids)
            self.room_group_name = f'chat_{shortuuid.uuid(name=room_identifier)}'
            logger.info(f"WebSocket connect: room name: {self.room_group_name}")
        except Exception as e:
            logger.error(f"WebSocket connect: Error creating room name for users {self.user.id}, {self.interlocutor_id}: {e}. Closing.")
            await self.close()
            return

        try:
            await self.channel_layer.group_add( #Создание канала
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket connect: Added channel {self.channel_name} to group '{self.room_group_name}'.")
        except Exception as e:
             logger.error(f"WebSocket connect: Failed to add channel to group '{self.room_group_name}': {e}. Closing.")
             await self.close()
             return

        await self.accept() #Принятие соединения
        logger.info(f"WebSocket connect: Connection accepted for user {self.user.id} in room {self.room_group_name}")

    @database_sync_to_async
    def get_interlocutor_user(self, user_id): #Получение айди собеседника
         try:
             return User.objects.get(id=user_id)
         except User.DoesNotExist:
             logger.warning(f"get_interlocutor_user: User with ID {user_id} not found.")
             return None

    @database_sync_to_async
    def check_friendship(self): #Проверка дружбы
        if not hasattr(self, 'user') or not hasattr(self, 'interlocutor') or not self.user or not self.interlocutor:
            logger.error("check_friendship: User or interlocutor not available.")
            return False
        try:
            return Friendship.objects.filter(
                (Q(from_user=self.user, to_user=self.interlocutor) |
                 Q(from_user=self.interlocutor, to_user=self.user)),
                status='accepted'
            ).exists()
        except Exception as e:
            logger.exception(
                f"check_friendship: Error checking friendship for users {self.user.id}, {self.interlocutor_id}: {e}")
            return False

    @database_sync_to_async
    def get_conversation_history(self, user1, user2, limit=10): #Для ии. Получение последних сообщений
        if not user1 or not user2:
            logger.error("get_conversation_history: Не предоставлены объекты пользователей.")
            return []

        try:
            messages = Message.objects.filter(
                (Q(sender=user1, receiver=user2) |
                 Q(sender=user2, receiver=user1))
            ).select_related('sender')
            recent_messages_desc = messages.order_by('-timestamp')[:limit]
            conversation_history_list = list(recent_messages_desc[::-1])

            logger.info(
                f"get_conversation_history: Получено {len(conversation_history_list)} последних сообщений")

            return conversation_history_list

        except Exception as e:
            logger.exception(
                f"get_conversation_history: Ошибка при получении сообщений между {user1.id} и {user2.id}: {e}")
            return []

    async def disconnect(self, close_code): #Отключение
        logger.info(
            f"WebSocket disconnect: User {self.user.id if hasattr(self, 'user') and self.user else 'N/A'} disconnecting from room {getattr(self, 'room_group_name', 'N/A')}. Code: {close_code}")
        if hasattr(self, 'room_group_name'):
            try:
                await self.channel_layer.group_discard( #Отключение канала
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(
                    f"WebSocket disconnect: Discarded channel {self.channel_name} from group '{self.room_group_name}'.")
            except Exception as e:
                logger.error(f"WebSocket disconnect: Error discarding channel from group '{self.room_group_name}': {e}")

    async def receive(self, text_data): #Получение текстового сообщения
        logger.info(f"WebSocket receive: Raw data from {self.user.id}: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message_text = text_data_json.get('message')

            if not message_text or not message_text.strip():
                logger.warning(f"WebSocket receive: Empty from {self.user.id}")
                return

            cleaned_message_text = message_text.strip()
            logger.info(f"WebSocket receive: message '{cleaned_message_text}' from {self.user.id}")

            message = await self.create_message(cleaned_message_text, sender=self.user, receiver=self.interlocutor) #Создание сообщения

            if message:
                message_data_for_group = {
                    'type': 'chat_message',
                    'message': message.text,
                    'sender_id': message.sender.id,
                    'timestamp': message.timestamp.isoformat(),
                    'sender_name': message.sender.full_name,
                }
                await self.channel_layer.group_send( #Отправка
                    self.room_group_name,
                    message_data_for_group
                )
                logger.info(
                    f"WebSocket receive: sent'{self.room_group_name}' from {self.user.id}.")

                if hasattr(self.interlocutor, 'is_ai') and self.interlocutor.is_ai:
                    logger.info(f"WebSocket receive: AI chat")
                    try:
                        conversation_history = await self.get_conversation_history(self.user, self.interlocutor, limit=10)

                        ai_response_text = await get_ai_response(  #Получение ответа нейросети
                            cleaned_message_text,
                            conversation_history,
                            self.ai_tokenizer,
                            self.ai_model,
                            self.ai_device
                        )

                        if ai_response_text:
                            logger.info(f"WebSocket receive: got from ai: '{ai_response_text}'")
                            ai_message = await self.create_message(ai_response_text, sender=self.interlocutor, receiver=self.user)

                            if ai_message:
                                ai_message_data_for_group = {
                                    'type': 'chat_message',
                                    'message': ai_message.text,
                                    'sender_id': ai_message.sender.id,  # ID пользователя-нейросети
                                    'timestamp': ai_message.timestamp.isoformat(),
                                    'sender_name': ai_message.sender.full_name,  # Имя пользователя-нейросети
                                }
                                await self.channel_layer.group_send(
                                    self.room_group_name,
                                    ai_message_data_for_group
                                )
                                logger.info(f"WebSocket receive: AI msg to '{self.room_group_name}'.")
                            else:
                                logger.error("WebSocket receive: Error with adding msg to db.")
                        else:
                            logger.warning("WebSocket receive:Empty from AI")

                    except Exception as e:
                        logger.exception(f"WebSocket receive: Error with AI: {e}")
            else:
                logger.error(f"WebSocket receive: error with msg of {self.user.id}: '{cleaned_message_text}'")


        except json.JSONDecodeError:
            logger.error(f"WebSocket receive: Invalid JSON {self.user.id}: '{text_data}'")
        except Exception as e:
            logger.exception(
                f"WebSocket receive: Error with msg {self.user.id}: '{text_data}'. Ошибка: {e}")

    @database_sync_to_async
    def create_message(self, text, sender, receiver): #Создание сообщения
        if not sender or not receiver:
            logger.error("create_message: Не предоставлены объекты отправителя или получателя.")
            return None
        try:
            msg = Message.objects.create(
                sender=sender,
                receiver=receiver,
                text=text
            )
            logger.info(f"create_message: Сохранено сообщение id {msg.id} от {sender.id} до {receiver.id}. Текст: '{text}'")
            return msg
        except Exception as e:
            logger.exception(f"create_message: Ошибка при сохранении сообщения от {sender.id} до {receiver.id}. Текст: '{text}'. Ошибка: {e}")
            return None

    async def chat_message(self, event):
        logger.info(f"WebSocket chat_message: {self.channel_name}. Event: {event}")
        try: #Обработка сообщения
            message_text = event.get('message')
            sender_id = event.get('sender_id')
            timestamp_iso = event.get('timestamp')
            sender_name = event.get('sender_name')

            if message_text is None or sender_id is None or timestamp_iso is None or sender_name is None: #Все ли на месте
                 logger.error(f"WebSocket chat_message: Incomplete message data received from group for channel {self.channel_name}: {event}")
                 return

            data_to_send = { #Что нужно отправить
                'message': message_text,
                'sender_id': sender_id,
                'timestamp': timestamp_iso,
                'sender_name': sender_name,
            }

            await self.send(text_data=json.dumps(data_to_send))
            logger.info(f"WebSocket chat_message: Sent msg to client {self.channel_name}.")

        except Exception as e:
             logger.exception(f"WebSocket chat_message: Error sending message to client {self.channel_name}. Event: {event}. Error: {e}")


