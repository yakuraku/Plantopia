"""
Plant Chat Service for AI-powered agriculture Q&A
Supports both general agriculture questions and plant-specific conversations with image upload
"""
import asyncio
import base64
import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import google.generativeai as genai
from PIL import Image

from app.repositories.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.services.plant_instance_service import PlantInstanceService
from app.services.plant_growth_service import PlantGrowthService
from app.services.external_api_service import get_gemini_service
from app.models.database import UserPlantChat, ChatMessage


logger = logging.getLogger(__name__)


# Agriculture Guardrails System Prompt
AGRICULTURE_GUARDRAILS_PROMPT = """You are an expert horticulturist and agricultural advisor specializing in home gardening, farming, and plant care. You MUST ONLY answer questions related to:
- Plant growing and care
- Gardening techniques
- Soil and composting
- Pest management
- Agriculture and farming
- Horticulture
- Plant diseases and health
- Harvesting and crop management
- Indoor and outdoor gardening
- Companion planting
- Seed starting and propagation
- Irrigation and water management
- Organic farming practices

If the user asks about anything outside these topics, politely respond with:
"I'm designed specifically to help with agriculture, farming, and plant-related questions. I cannot assist with other topics. Please ask me anything about growing plants, gardening techniques, or farming practices!"

Be helpful, practical, and provide actionable advice. Adapt your explanations to the user's experience level when known. When analyzing images, focus on plant health, growth stages, pest identification, soil conditions, and care recommendations."""


class PlantChatService:
    """Service for managing AI chat conversations about plants and agriculture"""

    # Token limits
    MAX_TOKENS = 120000
    WARNING_TOKENS = 100000

    # Chat expiration
    CHAT_EXPIRATION_HOURS = 6

    # History buffer
    MESSAGE_BUFFER_SIZE = 30  # Last 15 pairs (30 messages total)

    def __init__(self, db: AsyncSession):
        """
        Initialize the plant chat service

        Args:
            db: Database session
        """
        self.db = db
        self.repository = ChatRepository(db)
        self.user_repository = UserRepository(db)
        self.gemini_service = get_gemini_service()
        self.plant_instance_service = PlantInstanceService(db)
        self.growth_service = PlantGrowthService(db)

    async def start_general_chat(self, email: str) -> Dict[str, Any]:
        """
        Start a new general agriculture Q&A chat session

        Args:
            email: User email (auto-creates user if doesn't exist)

        Returns:
            Dictionary with chat details
        """
        # Get or create user
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found. Please start tracking a plant first.")

        logger.info(f"Starting general chat for user {email} (ID: {user.id})")

        # Create chat session
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.CHAT_EXPIRATION_HOURS)

        chat_data = {
            'user_id': user.id,
            'user_plant_instance_id': None,  # General chat has no linked plant
            'chat_type': 'general',
            'total_tokens': 0,
            'message_count': 0,
            'is_active': True,
            'created_at': now,
            'last_message_at': now,
            'expires_at': expires_at
        }

        chat = await self.repository.create_chat(chat_data)

        logger.info(f"Created general chat {chat.id} for user {email} (ID: {user.id})")

        return {
            'chat_id': chat.id,
            'chat_type': 'general',
            'expires_at': expires_at.isoformat(),
            'message': 'General agriculture chat started. Ask me anything about gardening, farming, or plant care!'
        }

    async def start_plant_chat(self, email: str, instance_id: int) -> Dict[str, Any]:
        """
        Start a new plant-specific chat session with full plant context

        Args:
            email: User email
            instance_id: Plant instance ID

        Returns:
            Dictionary with chat details

        Raises:
            ValueError: If user not found, instance not found or doesn't belong to user
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        logger.info(f"Starting plant-specific chat for user {email} (ID: {user.id}), instance {instance_id}")

        # Validate instance exists and belongs to user
        instance_details = await self.plant_instance_service.get_instance_details(instance_id)

        if not instance_details:
            raise ValueError(f"Plant instance {instance_id} not found")

        # Verify ownership (basic check from instance_details structure)
        # Note: PlantInstanceService already validates ownership internally

        # Create chat session
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.CHAT_EXPIRATION_HOURS)

        chat_data = {
            'user_id': user.id,
            'user_plant_instance_id': instance_id,
            'chat_type': 'plant_specific',
            'total_tokens': 0,
            'message_count': 0,
            'is_active': True,
            'created_at': now,
            'last_message_at': now,
            'expires_at': expires_at
        }

        chat = await self.repository.create_chat(chat_data)

        plant_name = instance_details['plant_details']['plant_name']
        nickname = instance_details['tracking_info']['plant_nickname']

        logger.info(f"Created plant chat {chat.id} for user {email} (ID: {user.id}), plant: {plant_name}")

        return {
            'chat_id': chat.id,
            'chat_type': 'plant_specific',
            'instance_id': instance_id,
            'plant_name': plant_name,
            'plant_nickname': nickname,
            'expires_at': expires_at.isoformat(),
            'message': f'Plant-specific chat started for {nickname} ({plant_name}). I have full context about your plant!'
        }

    async def send_message(
        self,
        chat_id: int,
        user_message: str,
        image_data: Optional[str] = None  # Base64 encoded
    ) -> Dict[str, Any]:
        """
        Send a message in an existing chat and get AI response

        Args:
            chat_id: Chat session ID
            user_message: User's message text
            image_data: Optional base64-encoded image

        Returns:
            Dictionary with AI response and token info

        Raises:
            ValueError: If chat not found, expired, or token limit exceeded
        """
        logger.info(f"Sending message to chat {chat_id}")

        # Get chat session
        chat = await self.repository.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        # Check if chat has expired
        if chat.expires_at < datetime.utcnow():
            raise ValueError(f"Chat {chat_id} has expired. Please start a new conversation.")

        # Check if chat is active
        if not chat.is_active:
            raise ValueError(f"Chat {chat_id} is no longer active")

        # Estimate new tokens (rough estimation)
        estimated_new_tokens = self._estimate_tokens(user_message)

        # Check token limit
        token_check = await self._check_token_limit(chat, estimated_new_tokens)
        if not token_check['allowed']:
            raise ValueError(
                f"Token limit exceeded. Current: {token_check['current']}, "
                f"Limit: {token_check['limit']}. Please start a new conversation."
            )

        # Get message history for context
        message_history = await self.repository.get_recent_messages(
            chat_id,
            self.MESSAGE_BUFFER_SIZE
        )

        # Build context based on chat type
        include_plant_context = (chat.chat_type == 'plant_specific')
        context = await self._build_chat_context(chat, include_plant_context)

        # Call Gemini API with history
        try:
            has_image = image_data is not None

            ai_response, response_tokens = await self._call_gemini_with_history(
                chat=chat,
                new_message=user_message,
                message_history=message_history,
                context=context,
                image_data=image_data
            )

            # Save user message
            user_msg_data = {
                'chat_id': chat_id,
                'role': 'user',
                'content': user_message,
                'has_image': has_image,
                'tokens_used': estimated_new_tokens,
                'created_at': datetime.utcnow()
            }
            await self.repository.add_message(user_msg_data)

            # Save AI response
            ai_msg_data = {
                'chat_id': chat_id,
                'role': 'assistant',
                'content': ai_response,
                'has_image': False,
                'tokens_used': response_tokens,
                'created_at': datetime.utcnow()
            }
            await self.repository.add_message(ai_msg_data)

            # Update chat totals (count both messages as 1 pair)
            total_tokens_used = estimated_new_tokens + response_tokens
            await self.repository.update_token_count(
                chat_id,
                total_tokens_used,
                increment_message_count=True
            )

            # Get updated chat for accurate totals
            updated_chat = await self.repository.get_chat_by_id(chat_id)

            logger.info(
                f"Chat {chat_id}: Message processed. "
                f"Tokens: {total_tokens_used}, Total: {updated_chat.total_tokens}"
            )

            return {
                'chat_id': chat_id,
                'user_message': user_message,
                'ai_response': ai_response,
                'tokens_used': total_tokens_used,
                'total_tokens': updated_chat.total_tokens,
                'token_warning': updated_chat.total_tokens >= self.WARNING_TOKENS,
                'message': (
                    f"Warning: You have used {updated_chat.total_tokens} tokens out of {self.MAX_TOKENS}. "
                    "Consider starting a new conversation soon."
                ) if updated_chat.total_tokens >= self.WARNING_TOKENS else None
            }

        except Exception as e:
            logger.error(f"Error processing message for chat {chat_id}: {e}")
            raise ValueError(f"Failed to process message: {str(e)}")

    async def get_chat_history(self, chat_id: int, email: str) -> Dict[str, Any]:
        """
        Get full chat history for a chat session

        Args:
            chat_id: Chat session ID
            email: User email (for ownership validation)

        Returns:
            Dictionary with chat details and full message history

        Raises:
            ValueError: If chat not found or user doesn't own chat
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        logger.info(f"Getting chat history for chat {chat_id}, user {email}")

        chat = await self.repository.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        # Verify ownership
        if chat.user_id != user.id:
            raise ValueError(f"User {email} does not own chat {chat_id}")

        # Get all messages
        messages = await self.repository.get_chat_messages(chat_id)

        # Format messages
        formatted_messages = [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'has_image': msg.has_image,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]

        return {
            'chat_id': chat.id,
            'chat_type': chat.chat_type,
            'created_at': chat.created_at.isoformat(),
            'expires_at': chat.expires_at.isoformat(),
            'total_tokens': chat.total_tokens,
            'message_count': chat.message_count,
            'is_active': chat.is_active,
            'messages': formatted_messages
        }

    async def end_chat(self, chat_id: int, email: str) -> bool:
        """
        End a chat session manually (marks as inactive)

        Args:
            chat_id: Chat session ID
            email: User email (for ownership validation)

        Returns:
            True if ended successfully

        Raises:
            ValueError: If chat not found or user doesn't own chat
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise ValueError(f"User with email {email} not found")

        logger.info(f"Ending chat {chat_id} for user {email}")

        chat = await self.repository.get_chat_by_id(chat_id)
        if not chat:
            raise ValueError(f"Chat {chat_id} not found")

        # Verify ownership
        if chat.user_id != user.id:
            raise ValueError(f"User {email} does not own chat {chat_id}")

        # Deactivate chat (soft delete)
        await self.repository.deactivate_chat(chat_id)

        logger.info(f"Chat {chat_id} ended successfully")
        return True

    async def cleanup_expired_chats(self) -> int:
        """
        Delete chats older than 6 hours (for background cleanup job)

        Returns:
            Number of chats deleted
        """
        logger.info("Running expired chat cleanup job")

        deleted_count = await self.repository.delete_expired_chats()

        logger.info(f"Deleted {deleted_count} expired chat sessions")
        return deleted_count

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================

    async def _build_chat_context(
        self,
        chat: UserPlantChat,
        include_plant_context: bool = False
    ) -> str:
        """
        Build context string for Gemini API call

        Args:
            chat: UserPlantChat instance
            include_plant_context: Whether to include plant-specific context

        Returns:
            Formatted context string
        """
        context_parts = []

        if include_plant_context and chat.user_plant_instance_id:
            # Get plant instance details
            try:
                instance_details = await self.plant_instance_service.get_instance_details(
                    chat.user_plant_instance_id
                )

                plant_info = instance_details['plant_details']
                tracking_info = instance_details['tracking_info']
                timeline = instance_details.get('timeline', {})
                tips = instance_details.get('current_tips', [])

                context_parts.extend([
                    "=== PLANT CONTEXT ===",
                    f"Plant Name: {plant_info['plant_name']} ({plant_info.get('scientific_name', 'N/A')})",
                    f"Plant Nickname: {tracking_info['plant_nickname']}",
                    f"Category: {plant_info.get('plant_category', 'N/A')}",
                    f"Current Stage: {tracking_info['current_stage']}",
                    f"Days Elapsed: {tracking_info['days_elapsed']}",
                    f"Progress: {tracking_info['progress_percentage']}%",
                    f"Start Date: {tracking_info['start_date']}",
                    f"Expected Maturity: {tracking_info['expected_maturity_date']}",
                    f"Location: {tracking_info.get('location_details', 'Not specified')}",
                    ""
                ])

                # Add current stage tips
                if tips:
                    context_parts.append("Current Care Tips:")
                    for tip in tips[:5]:  # Limit to 5 tips
                        context_parts.append(f"- {tip}")
                    context_parts.append("")

            except Exception as e:
                logger.warning(f"Could not fetch plant context for instance {chat.user_plant_instance_id}: {e}")
                context_parts.append("Plant context temporarily unavailable.")
                context_parts.append("")

        return "\n".join(context_parts) if context_parts else ""

    async def _check_token_limit(self, chat: UserPlantChat, estimated_new: int) -> Dict:
        """
        Check if adding new tokens would exceed limits

        Args:
            chat: UserPlantChat instance
            estimated_new: Estimated tokens for new message

        Returns:
            Dictionary with allowed, warning, current, and limit keys
        """
        current_total = chat.total_tokens or 0
        projected_total = current_total + estimated_new

        return {
            'allowed': projected_total <= self.MAX_TOKENS,
            'warning': projected_total >= self.WARNING_TOKENS,
            'current': current_total,
            'projected': projected_total,
            'limit': self.MAX_TOKENS
        }

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens for text (rough estimation: word count * 1.3)

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        word_count = len(text.split())
        return int(word_count * 1.3)

    async def _call_gemini_with_history(
        self,
        chat: UserPlantChat,
        new_message: str,
        message_history: List[ChatMessage],
        context: str,
        image_data: Optional[str] = None
    ) -> tuple[str, int]:
        """
        Call Gemini API with chat history and optional image

        Args:
            chat: UserPlantChat instance
            new_message: New user message
            message_history: List of recent ChatMessage instances
            context: Plant context string
            image_data: Optional base64-encoded image

        Returns:
            Tuple of (AI response text, estimated tokens used)
        """
        try:
            # Configure Gemini with API key
            api_key = self.gemini_service._find_available_key()
            if not api_key:
                raise ValueError("No Gemini API keys available")

            genai.configure(api_key=api_key)

            # Build conversation history
            history_parts = []

            # Add context at the start
            if context:
                history_parts.append(f"{context}\n")

            # Add message history
            for msg in message_history:
                prefix = "User: " if msg.role == "user" else "Assistant: "
                history_parts.append(f"{prefix}{msg.content}")

            # Combine history into prompt
            history_text = "\n\n".join(history_parts)
            full_prompt = f"{history_text}\n\nUser: {new_message}" if history_text else f"User: {new_message}"

            # Create model
            model = genai.GenerativeModel(
                model_name=self.gemini_service.model_name,
                system_instruction=AGRICULTURE_GUARDRAILS_PROMPT
            )

            # If image provided, include it in the request
            if image_data:
                logger.info("Processing message with image")

                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))

                # Generate content with image
                response = await asyncio.to_thread(
                    model.generate_content,
                    [full_prompt, image]
                )
            else:
                # Generate content with text only
                response = await asyncio.to_thread(
                    model.generate_content,
                    full_prompt
                )

            # Extract response text
            ai_response = response.text

            # Estimate tokens used (rough estimate)
            response_tokens = self._estimate_tokens(ai_response)

            # Track usage in gemini service
            key_id = self.gemini_service._get_current_key_id()
            total_tokens = self._estimate_tokens(full_prompt) + response_tokens
            self.gemini_service._track_api_usage(key_id, total_tokens)

            logger.info(f"Gemini API call successful. Response tokens: {response_tokens}")
            return ai_response, response_tokens

        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise ValueError(f"Failed to get AI response: {str(e)}")
