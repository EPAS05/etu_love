import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from channels.db import database_sync_to_async
from authuser.models import User
from compatibility.models import Friendship
from messenger.models import Message
import shortuuid
import logging
import asyncio

logger = logging.getLogger(__name__)

async def get_ai_response(message_text, conversation_history):
    logger.info(f"Вызов заглушки нейросети с сообщением: '{message_text}'")
    await asyncio.sleep(2)
    logger.info(f"Заглушка нейросети сгенерировала ответ.")

    return f"Я, нейросеть, получил ваше сообщение: '{message_text}'"

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        logger.info(f"WebSocket connect: Attempt. User: {self.user}, Authenticated: {self.user.is_authenticated}")
        if not self.user or not self.user.is_authenticated:
            logger.warning("WebSocket connect: Unauthenticated user attempt. Closing.")
            await self.close()
            return

        try:
            self.interlocutor_id = int(self.scope['url_route']['kwargs']['user_id'])
            self.interlocutor = await self.get_interlocutor_user(self.interlocutor_id)

            if not self.interlocutor:
                 logger.warning(f"WebSocket connect: Interlocutor user {self.interlocutor_id} not found. Closing.")
                 await self.close()
                 return

        except (ValueError, KeyError) as e:
             logger.error(f"WebSocket connect: Error getting interlocutor ID: {e}. Closing.")
             await self.close()
             return
        except User.DoesNotExist:
             logger.warning(f"WebSocket connect: Interlocutor user {self.interlocutor_id} not found (DoesNotExist). Closing.")
             await self.close()
             return


        logger.info(f"WebSocket connect: User '{self.user.email}' (ID: {self.user.id}) attempting connection with User ID: {self.interlocutor_id}")

        is_friend = await self.check_friendship()
        is_interlocutor_ai = hasattr(self.interlocutor, 'is_ai') and self.interlocutor.is_ai
        if not is_friend and not is_interlocutor_ai:
            logger.warning(f"WebSocket connect: User {self.user.id} и {self.interlocutor_id} не друзья И собеседник не нейросеть. Закрытие соединения.")
            await self.close()
            return

        try:
            user_ids = sorted([str(self.user.id), str(self.interlocutor_id)])
            room_identifier = "-".join(user_ids)
            self.room_group_name = f'chat_{shortuuid.uuid(name=room_identifier)}'
            logger.info(f"WebSocket connect: Calculated room name: {self.room_group_name}")
        except Exception as e:
            logger.error(f"WebSocket connect: Error creating room name for users {self.user.id}, {self.interlocutor_id}: {e}. Closing.")
            await self.close()
            return

        try:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket connect: Added channel {self.channel_name} to group '{self.room_group_name}'.")
        except Exception as e:
             logger.error(f"WebSocket connect: Failed to add channel to group '{self.room_group_name}': {e}. Closing.")
             await self.close()
             return

        await self.accept()
        logger.info(f"WebSocket connect: Connection accepted for user {self.user.id} in room {self.room_group_name}")

    @database_sync_to_async
    def get_interlocutor_user(self, user_id):
         try:
             return User.objects.get(id=user_id)
         except User.DoesNotExist:
             logger.warning(f"get_interlocutor_user: User with ID {user_id} not found.")
             return None

    @database_sync_to_async
    def check_friendship(self):
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

    async def disconnect(self, close_code):
        logger.info(
            f"WebSocket disconnect: User {self.user.id if hasattr(self, 'user') and self.user else 'N/A'} disconnecting from room {getattr(self, 'room_group_name', 'N/A')}. Code: {close_code}")
        if hasattr(self, 'room_group_name'):
            try:
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )
                logger.info(
                    f"WebSocket disconnect: Discarded channel {self.channel_name} from group '{self.room_group_name}'.")
            except Exception as e:
                logger.error(f"WebSocket disconnect: Error discarding channel from group '{self.room_group_name}': {e}")

    async def receive(self, text_data):
        logger.info(f"WebSocket receive: Raw data from {self.user.id}: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message_text = text_data_json.get('message')

            if not message_text or not message_text.strip():
                logger.warning(f"WebSocket receive: Empty or missing 'message' field from {self.user.id}. Ignoring.")
                return

            cleaned_message_text = message_text.strip()
            logger.info(f"WebSocket receive: Processed message '{cleaned_message_text}' from {self.user.id}")

            message = await self.create_message(cleaned_message_text, sender=self.user, receiver=self.interlocutor)

            if message:
                message_data_for_group = {
                    'type': 'chat_message',
                    'message': message.text,
                    'sender_id': message.sender.id,
                    'timestamp': message.timestamp.isoformat(),
                    'sender_name': message.sender.full_name,
                }
                await self.channel_layer.group_send(
                    self.room_group_name,
                    message_data_for_group
                )
                logger.info(
                    f"WebSocket receive: Сообщение пользователя отправлено в группу '{self.room_group_name}' от {self.user.id}.")

                if hasattr(self.interlocutor, 'is_ai') and self.interlocutor.is_ai:
                    logger.info(
                        f"WebSocket receive: Чат с нейросетью ({self.interlocutor.full_name}). Запускаем логику ответа нейросети.")
                    try:
                        conversation_history = []
                        ai_response_text = await get_ai_response(cleaned_message_text, conversation_history)

                        if ai_response_text:
                            logger.info(f"WebSocket receive: Получен ответ от нейросети: '{ai_response_text}'")
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
                                logger.info(
                                    f"WebSocket receive: Сообщение нейросети отправлено в группу '{self.room_group_name}'.")
                            else:
                                logger.error("WebSocket receive: Не удалось создать сообщение нейросети в БД.")
                        else:
                            logger.warning("WebSocket receive: Функция нейросети вернула пустой ответ.")

                    except Exception as e:
                        logger.exception(f"WebSocket receive: Ошибка при вызове или обработке ответа нейросети: {e}")
            else:
                logger.error(
                    f"WebSocket receive: Не удалось создать сообщение пользователя в БД для {self.user.id}. Текст: '{cleaned_message_text}'")


        except json.JSONDecodeError:
            logger.error(f"WebSocket receive: Получен невалидный JSON от {self.user.id}: '{text_data}'")
        except Exception as e:
            logger.exception(
                f"WebSocket receive: Неожиданная ошибка при обработке сообщения от {self.user.id}. Данные: '{text_data}'. Ошибка: {e}")

    @database_sync_to_async
    def create_message(self, text, sender, receiver):
        if not sender or not receiver:
            logger.error("create_message: Не предоставлены объекты отправителя или получателя.")
            return None
        try:
            msg = Message.objects.create(
                sender=sender,
                receiver=receiver,
                text=text
            )
            logger.info(
                f"create_message: Сохранено сообщение id {msg.id} от {sender.id} до {receiver.id}. Текст: '{text}'")
            return msg
        except Exception as e:
            logger.exception(
                f"create_message: Ошибка при сохранении сообщения от {sender.id} до {receiver.id}. Текст: '{text}'. Ошибка: {e}")
            return None

    async def chat_message(self, event):
        logger.info(f"WebSocket chat_message: Received message from group for channel {self.channel_name}. Event: {event}")
        try:
            message_text = event.get('message')
            sender_id = event.get('sender_id')
            timestamp_iso = event.get('timestamp')
            sender_name = event.get('sender_name')

            if message_text is None or sender_id is None or timestamp_iso is None or sender_name is None: # <--- ВКЛЮЧАЕМ sender_name в проверку
                 logger.error(f"WebSocket chat_message: Incomplete message data received from group for channel {self.channel_name}: {event}")
                 return

            data_to_send = {
                'message': message_text,
                'sender_id': sender_id,
                'timestamp': timestamp_iso,
                'sender_name': sender_name,
            }

            await self.send(text_data=json.dumps(data_to_send))
            logger.info(f"WebSocket chat_message: Sent message to client {self.channel_name}.")

        except Exception as e:
             logger.exception(f"WebSocket chat_message: Error sending message to client {self.channel_name}. Event: {event}. Error: {e}")


