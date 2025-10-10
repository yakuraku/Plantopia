"""
Chat Repository for managing chat and chat message operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, delete
from sqlalchemy.orm import selectinload
from app.models.database import UserPlantChat, ChatMessage, User, UserPlantInstance


class ChatRepository:
    """Repository for managing chat database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ============================================================================
    # CHAT CRUD OPERATIONS
    # ============================================================================

    async def create_chat(self, chat_data: Dict[str, Any]) -> UserPlantChat:
        """
        Create new chat session

        Args:
            chat_data: Dictionary containing chat information

        Returns:
            Created UserPlantChat instance
        """
        chat = UserPlantChat(**chat_data)

        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)

        return chat

    async def get_chat_by_id(self, chat_id: int) -> Optional[UserPlantChat]:
        """
        Get chat by ID with related data

        Args:
            chat_id: Chat ID

        Returns:
            UserPlantChat instance or None if not found
        """
        query = select(UserPlantChat).options(
            selectinload(UserPlantChat.user),
            selectinload(UserPlantChat.plant_instance),
            selectinload(UserPlantChat.messages)
        ).where(UserPlantChat.id == chat_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_chats(
        self,
        user_id: int,
        active_only: bool = True,
        chat_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[UserPlantChat]:
        """
        Get all chat sessions for a user

        Args:
            user_id: User ID
            active_only: If True, only return active chats
            chat_type: Optional filter by chat type ('general' or 'plant_specific')
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of UserPlantChat instances
        """
        query = select(UserPlantChat).options(
            selectinload(UserPlantChat.plant_instance)
        ).where(UserPlantChat.user_id == user_id)

        if active_only:
            query = query.where(UserPlantChat.is_active == True)

        if chat_type:
            query = query.where(UserPlantChat.chat_type == chat_type)

        query = query.order_by(desc(UserPlantChat.last_message_at)).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_chat(self, chat_id: int, update_data: Dict[str, Any]) -> UserPlantChat:
        """
        Update chat session

        Args:
            chat_id: Chat ID
            update_data: Dictionary containing updated information

        Returns:
            Updated UserPlantChat instance

        Raises:
            ValueError: If chat not found
        """
        chat = await self.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError(f"Chat with ID {chat_id} not found")

        # Update fields
        for key, value in update_data.items():
            if hasattr(chat, key) and value is not None:
                setattr(chat, key, value)

        await self.db.commit()
        await self.db.refresh(chat)

        return chat

    async def delete_chat(self, chat_id: int) -> bool:
        """
        Delete a chat session (hard delete, cascade deletes messages)

        Args:
            chat_id: Chat ID

        Returns:
            True if deleted, False if not found
        """
        chat = await self.get_chat_by_id(chat_id)

        if chat:
            await self.db.delete(chat)
            await self.db.commit()
            return True

        return False

    async def update_token_count(
        self,
        chat_id: int,
        tokens_to_add: int,
        increment_message_count: bool = True
    ) -> UserPlantChat:
        """
        Update token count and message count for a chat

        Args:
            chat_id: Chat ID
            tokens_to_add: Number of tokens to add to total
            increment_message_count: Whether to increment message count

        Returns:
            Updated UserPlantChat instance

        Raises:
            ValueError: If chat not found
        """
        chat = await self.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError(f"Chat with ID {chat_id} not found")

        chat.total_tokens = (chat.total_tokens or 0) + tokens_to_add
        if increment_message_count:
            chat.message_count = (chat.message_count or 0) + 1
        chat.last_message_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(chat)

        return chat

    # ============================================================================
    # MESSAGE CRUD OPERATIONS
    # ============================================================================

    async def add_message(self, message_data: Dict[str, Any]) -> ChatMessage:
        """
        Add a new message to a chat

        Args:
            message_data: Dictionary containing message information

        Returns:
            Created ChatMessage instance
        """
        message = ChatMessage(**message_data)

        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def get_chat_messages(
        self,
        chat_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ChatMessage]:
        """
        Get messages for a chat session

        Args:
            chat_id: Chat ID
            limit: Maximum number of messages to return (None for all)
            offset: Number of messages to skip

        Returns:
            List of ChatMessage instances ordered by creation time
        """
        query = select(ChatMessage).where(
            ChatMessage.chat_id == chat_id
        ).order_by(ChatMessage.created_at)

        if limit is not None:
            query = query.limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_messages(
        self,
        chat_id: int,
        message_count: int = 20
    ) -> List[ChatMessage]:
        """
        Get the most recent N messages for a chat (for history buffer)

        Args:
            chat_id: Chat ID
            message_count: Number of recent messages to retrieve

        Returns:
            List of ChatMessage instances ordered by creation time (oldest to newest)
        """
        query = select(ChatMessage).where(
            ChatMessage.chat_id == chat_id
        ).order_by(desc(ChatMessage.created_at)).limit(message_count)

        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        # Reverse to get chronological order (oldest to newest)
        return list(reversed(messages))

    async def count_messages(self, chat_id: int) -> int:
        """
        Count total messages in a chat

        Args:
            chat_id: Chat ID

        Returns:
            Total message count
        """
        query = select(func.count(ChatMessage.id)).where(
            ChatMessage.chat_id == chat_id
        )

        result = await self.db.execute(query)
        return result.scalar_one()

    # ============================================================================
    # CLEANUP AND MAINTENANCE
    # ============================================================================

    async def delete_expired_chats(self, current_time: Optional[datetime] = None) -> int:
        """
        Delete chat sessions that have expired (for background cleanup job)

        Args:
            current_time: Current time (defaults to now)

        Returns:
            Number of chats deleted
        """
        if current_time is None:
            current_time = datetime.utcnow()

        # Find expired chats
        query = select(UserPlantChat).where(
            UserPlantChat.expires_at < current_time
        )

        result = await self.db.execute(query)
        expired_chats = result.scalars().all()

        # Delete each chat (cascade will delete messages)
        deleted_count = 0
        for chat in expired_chats:
            await self.db.delete(chat)
            deleted_count += 1

        await self.db.commit()

        return deleted_count

    async def deactivate_chat(self, chat_id: int) -> UserPlantChat:
        """
        Mark a chat as inactive (soft delete)

        Args:
            chat_id: Chat ID

        Returns:
            Updated UserPlantChat instance

        Raises:
            ValueError: If chat not found
        """
        return await self.update_chat(chat_id, {'is_active': False})

    async def get_chat_with_instance(
        self,
        user_id: int,
        instance_id: int,
        active_only: bool = True
    ) -> Optional[UserPlantChat]:
        """
        Get existing chat for a specific user and plant instance

        Args:
            user_id: User ID
            instance_id: Plant instance ID
            active_only: If True, only return active chats

        Returns:
            UserPlantChat instance or None if not found
        """
        query = select(UserPlantChat).where(
            and_(
                UserPlantChat.user_id == user_id,
                UserPlantChat.user_plant_instance_id == instance_id
            )
        )

        if active_only:
            query = query.where(UserPlantChat.is_active == True)

        # Get most recent chat
        query = query.order_by(desc(UserPlantChat.created_at)).limit(1)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count_user_chats(
        self,
        user_id: int,
        active_only: bool = True,
        chat_type: Optional[str] = None
    ) -> int:
        """
        Count total chats for a user

        Args:
            user_id: User ID
            active_only: If True, only count active chats
            chat_type: Optional filter by chat type

        Returns:
            Total count
        """
        query = select(func.count(UserPlantChat.id)).where(
            UserPlantChat.user_id == user_id
        )

        if active_only:
            query = query.where(UserPlantChat.is_active == True)

        if chat_type:
            query = query.where(UserPlantChat.chat_type == chat_type)

        result = await self.db.execute(query)
        return result.scalar_one()
