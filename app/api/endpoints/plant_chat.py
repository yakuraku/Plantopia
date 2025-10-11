"""
Plant Chat API Endpoints
Handles AI-powered chat conversations for agriculture Q&A and plant-specific advice
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.schemas.plant_tracking import (
    StartChatRequest,
    StartChatResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatHistoryResponse,
    EndChatResponse,
    ErrorResponse
)
from app.services.plant_chat_service import PlantChatService
from app.core.database import get_async_db

router = APIRouter(tags=["plant-chat"])


# Dependency injection
async def get_plant_chat_service(
    db: AsyncSession = Depends(get_async_db)
) -> PlantChatService:
    """Get plant chat service instance"""
    return PlantChatService(db)


# ============================================================================
# GENERAL CHAT ENDPOINTS
# ============================================================================

@router.post("/chat/general/start", response_model=StartChatResponse, status_code=201)
async def start_general_chat(
    request: StartChatRequest,
    chat_service: PlantChatService = Depends(get_plant_chat_service)
):
    """
    Start a new general agriculture Q&A chat session.

    This endpoint:
    - Creates a new chat session for general agriculture questions
    - No plant context required - ask anything about gardening/farming
    - Chat auto-expires after 6 hours
    - Tracks token usage (120k limit per conversation)
    - AI applies agriculture-only guardrails (rejects non-farming topics)

    Args:
        request: Start chat request with email

    Returns:
        StartChatResponse with chat_id and expiration time

    Raises:
        HTTPException 404: If user not found
        HTTPException 500: If chat creation fails
    """
    try:
        result = await chat_service.start_general_chat(email=request.email)
        return StartChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting general chat: {str(e)}")


@router.post("/chat/general/message", response_model=ChatMessageResponse)
async def send_general_message(
    request: ChatMessageRequest,
    chat_service: PlantChatService = Depends(get_plant_chat_service)
):
    """
    Send a message in a general agriculture chat.

    This endpoint:
    - Sends user message to AI assistant
    - Supports optional image upload (base64 encoded)
    - Maintains conversation context (last 15 message pairs)
    - Returns AI response with token tracking
    - Warns when approaching 100k tokens (120k limit)

    Args:
        request: Chat message request with chat_id, message, and optional image

    Returns:
        ChatMessageResponse with AI response and token info

    Raises:
        HTTPException 404: If chat not found or expired
        HTTPException 400: If token limit exceeded
        HTTPException 500: If message processing fails
    """
    try:
        result = await chat_service.send_message(
            chat_id=request.chat_id,
            user_message=request.message,
            image_data=request.image
        )
        return ChatMessageResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg or "expired" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "token limit" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# ============================================================================
# PLANT-SPECIFIC CHAT ENDPOINTS
# ============================================================================

@router.post("/chat/plant/{instance_id}/start", response_model=StartChatResponse, status_code=201)
async def start_plant_chat(
    instance_id: int,
    request: StartChatRequest,
    chat_service: PlantChatService = Depends(get_plant_chat_service)
):
    """
    Start a new plant-specific chat session with full plant context.

    This endpoint:
    - Creates chat session linked to specific user plant instance
    - AI has full context: plant details, current stage, timeline, care tips
    - Provides personalized advice for user's specific plant
    - Chat auto-expires after 6 hours
    - Tracks token usage (120k limit per conversation)

    Args:
        instance_id: Plant instance ID to chat about
        request: Start chat request with email

    Returns:
        StartChatResponse with chat details and plant info

    Raises:
        HTTPException 404: If user or plant instance not found
        HTTPException 500: If chat creation fails
    """
    try:
        result = await chat_service.start_plant_chat(
            email=request.email,
            instance_id=instance_id
        )
        return StartChatResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting plant chat: {str(e)}")


@router.post("/chat/plant/message", response_model=ChatMessageResponse)
async def send_plant_message(
    request: ChatMessageRequest,
    chat_service: PlantChatService = Depends(get_plant_chat_service)
):
    """
    Send a message in a plant-specific chat.

    This endpoint:
    - Sends message with full plant context included
    - AI knows current stage, timeline, and plant-specific details
    - Supports optional image upload (e.g., plant health diagnosis)
    - Maintains conversation context (last 15 message pairs)
    - Returns AI response with token tracking

    Args:
        request: Chat message request with chat_id, message, and optional image

    Returns:
        ChatMessageResponse with AI response and token info

    Raises:
        HTTPException 404: If chat not found or expired
        HTTPException 400: If token limit exceeded
        HTTPException 500: If message processing fails
    """
    try:
        result = await chat_service.send_message(
            chat_id=request.chat_id,
            user_message=request.message,
            image_data=request.image
        )
        return ChatMessageResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg or "expired" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "token limit" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# ============================================================================
# CHAT MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/chat/{chat_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    chat_id: int,
    email: str = Query(..., description="User email for ownership validation"),
    chat_service: PlantChatService = Depends(get_plant_chat_service)
):
    """
    Get full chat history for a conversation.

    This endpoint:
    - Returns complete message history for a chat session
    - Validates user owns the chat
    - Includes all messages (user and assistant)
    - Shows chat metadata (type, tokens, expiration)
    - Useful for displaying conversation in UI

    Args:
        chat_id: Chat session ID
        email: User email (for ownership validation)

    Returns:
        ChatHistoryResponse with full conversation history

    Raises:
        HTTPException 404: If chat or user not found
        HTTPException 403: If user doesn't own chat
        HTTPException 500: If data retrieval fails
    """
    try:
        result = await chat_service.get_chat_history(chat_id=chat_id, email=email)
        return ChatHistoryResponse(**result)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "does not own" in error_msg:
            raise HTTPException(status_code=403, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading chat history: {str(e)}")


@router.delete("/chat/{chat_id}", response_model=EndChatResponse)
async def end_chat(
    chat_id: int,
    email: str = Query(..., description="User email for ownership validation"),
    chat_service: PlantChatService = Depends(get_plant_chat_service)
):
    """
    End a chat session manually.

    This endpoint:
    - Marks chat as inactive (soft delete)
    - Preserves message history for reference
    - Chat won't be automatically deleted until 6-hour expiration
    - User won't see inactive chats in their active chat list
    - Useful for ending conversations early

    Args:
        chat_id: Chat session ID to end
        email: User email (for ownership validation)

    Returns:
        EndChatResponse with success confirmation

    Raises:
        HTTPException 404: If chat not found
        HTTPException 403: If user doesn't own chat
        HTTPException 500: If operation fails
    """
    try:
        success = await chat_service.end_chat(chat_id=chat_id, email=email)
        return EndChatResponse(
            success=success,
            message=f"Chat {chat_id} ended successfully",
            chat_id=chat_id
        )
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "does not own" in error_msg:
            raise HTTPException(status_code=403, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ending chat: {str(e)}")
