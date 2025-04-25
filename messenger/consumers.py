import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from channels.db import database_sync_to_async
from authuser.models import User
from compatibility.models import Friendship
from messenger.models import Message
import shortuuid
import logging

logger = logging.getLogger(__name__)



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
        except User.DoesNotExist: # Catch if get_interlocutor_user returns None (handled above) or raises DoesNotExist (less likely with check)
             logger.warning(f"WebSocket connect: Interlocutor user {self.interlocutor_id} not found (DoesNotExist). Closing.")
             await self.close()
             return


        logger.info(f"WebSocket connect: User '{self.user.email}' (ID: {self.user.id}) attempting connection with User ID: {self.interlocutor_id}")

        # Check friendship - now calling the async method
        is_friend = await self.check_friendship()
        if not is_friend:
            logger.warning(f"WebSocket connect: User {self.user.id} and {self.interlocutor_id} are not friends. Closing connection.")
            await self.close() # Consider a specific close code > 4000
            return

        # --- Create Room Name ---
        try:
            # Sorted IDs for consistent room name
            user_ids = sorted([str(self.user.id), str(self.interlocutor_id)])
            room_identifier = "-".join(user_ids)
            # Use shortuuid based on sorted IDs
            self.room_group_name = f'chat_{shortuuid.uuid(name=room_identifier)}'
            logger.info(f"WebSocket connect: Calculated room name: {self.room_group_name}")
        except Exception as e:
            logger.error(f"WebSocket connect: Error creating room name for users {self.user.id}, {self.interlocutor_id}: {e}. Closing.")
            await self.close()
            return


        # --- Add Channel to Group ---
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

        # --- Accept Connection ---
        await self.accept()
        logger.info(f"WebSocket connect: Connection accepted for user {self.user.id} in room {self.room_group_name}")

    # --- Async Helper for getting Interlocutor User ---
    @database_sync_to_async
    def get_interlocutor_user(self, user_id):
         try:
             return User.objects.get(id=user_id)
         except User.DoesNotExist:
             logger.warning(f"get_interlocutor_user: User with ID {user_id} not found.")
             return None # Return None instead of raising DoesNotExist here

    @database_sync_to_async
    def check_friendship(self):
        # Ensure users are set before querying
        if not hasattr(self, 'user') or not hasattr(self, 'interlocutor') or not self.user or not self.interlocutor:
            logger.error("check_friendship: User or interlocutor not available.")
            return False
        try:
            # Use Q objects for OR condition
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
        # Remove channel from group if it was added
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

            message = await self.create_message(cleaned_message_text)

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
                logger.info(f"WebSocket receive: Message sent to group '{self.room_group_name}' by {self.user.id}.")
            else:
                 logger.error(f"WebSocket receive: Failed to create DB message for {self.user.id}. Text: '{cleaned_message_text}'")


        except json.JSONDecodeError:
             logger.error(f"WebSocket receive: Invalid JSON from {self.user.id}: '{text_data}'")
        except Exception as e:
             logger.exception(f"WebSocket receive: Unexpected error processing message from {self.user.id} in room {self.room_group_name}. Data: '{text_data}'. Error: {e}")


    # --- Async Helper for saving Message to DB ---
    @database_sync_to_async
    def create_message(self, text):
        # Ensure sender and receiver are available
        if not hasattr(self, 'user') or not hasattr(self, 'interlocutor') or not self.user or not self.interlocutor:
            logger.error("create_message: User or interlocutor not set.")
            return None
        try:
            # Save the message object
            msg = Message.objects.create(
                sender=self.user,
                receiver=self.interlocutor,
                text=text
            )
            logger.info(f"create_message: Saved message id {msg.id} from {self.user.id} to {self.interlocutor.id}. Text: '{text}'")
            return msg
        except Exception as e:
            logger.exception(f"create_message: Error saving message from {self.user.id} to {self.interlocutor.id}. Text: '{text}'. Error: {e}")
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


