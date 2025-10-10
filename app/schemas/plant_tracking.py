"""
Pydantic schemas for Plant Tracking Feature (Iteration 3)
Handles request/response validation for plant tracking endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class UserDataInput(BaseModel):
    """User data input from frontend for API context building"""
    email: str = Field(..., description="User email for identification")
    name: str = Field(..., description="User display name")
    suburb_id: int = Field(..., description="Location ID for climate data")
    experience_level: str = Field(default="beginner", description="Gardening expertise level")
    garden_type: str = Field(default="backyard", description="Growing environment type")
    available_space: float = Field(default=10.0, description="Available space in square meters")
    climate_goal: str = Field(default="general gardening", description="Environmental preferences")


class StartTrackingRequest(BaseModel):
    """Request to start tracking a new plant instance"""
    user_data: UserDataInput = Field(..., description="User context data")
    plant_id: int = Field(..., description="ID of plant to track")
    plant_nickname: str = Field(..., max_length=100, description="User's custom name for this plant")
    start_date: date = Field(..., description="Date when user started growing")
    location_details: Optional[str] = Field(None, max_length=200, description="Where planted (e.g., 'balcony pot 1')")


class UpdateProgressRequest(BaseModel):
    """Request to update plant instance progress"""
    current_stage: Optional[str] = Field(None, max_length=50, description="Current growth stage")
    user_notes: Optional[str] = Field(None, description="User's personal notes")
    location_details: Optional[str] = Field(None, max_length=200, description="Location where planted")


class CompleteChecklistItemRequest(BaseModel):
    """Request to mark a checklist item as complete"""
    instance_id: int = Field(..., description="User plant instance ID")
    checklist_item_key: str = Field(..., max_length=200, description="Unique key for checklist item")
    is_completed: bool = Field(..., description="Completion status")
    user_notes: Optional[str] = Field(None, description="User's notes about this item")


class UpdateNicknameRequest(BaseModel):
    """Request to update plant nickname"""
    plant_nickname: str = Field(..., max_length=100, description="New nickname for the plant")


# ============================================================================
# RESPONSE SCHEMAS - JSON Data Structures
# ============================================================================

class RequirementItem(BaseModel):
    """Individual requirement item"""
    item: str = Field(..., description="Name of required item")
    quantity: str = Field(..., description="Quantity needed")
    optional: bool = Field(..., description="Whether this item is optional")
    notes: Optional[str] = Field(None, description="Additional notes about this item")


class RequirementCategory(BaseModel):
    """Category of requirements"""
    category: str = Field(..., description="Category name (e.g., 'Seeds & Plants')")
    items: List[RequirementItem] = Field(..., description="List of items in this category")


class SetupInstruction(BaseModel):
    """Individual setup instruction step"""
    step: int = Field(..., description="Step number")
    title: str = Field(..., description="Step title")
    description: str = Field(..., description="Detailed description")
    duration: str = Field(..., description="Estimated duration")
    tips: List[str] = Field(..., description="Helpful tips for this step")
    warnings: Optional[List[str]] = Field(None, description="Warnings or cautions")


class GrowthStage(BaseModel):
    """Growth stage information"""
    stage_name: str = Field(..., description="Name of the stage")
    start_day: int = Field(..., description="Starting day of this stage")
    end_day: int = Field(..., description="Ending day of this stage")
    description: str = Field(..., description="Description of this stage")
    key_indicators: List[str] = Field(..., description="Visual indicators for this stage")
    stage_order: int = Field(..., description="Order of this stage in the timeline")


class CareTip(BaseModel):
    """Individual care tip"""
    tip: str = Field(..., description="The care tip text")
    category: str = Field(..., description="Category of tip (e.g., 'watering', 'sunlight')")
    importance: str = Field(..., description="Importance level (low, medium, high)")


class StageTips(BaseModel):
    """Tips for a specific growth stage"""
    stage_name: str = Field(..., description="Name of the stage")
    tips: List[CareTip] = Field(..., description="List of tips for this stage")


# ============================================================================
# RESPONSE SCHEMAS - API Responses
# ============================================================================

class StartTrackingResponse(BaseModel):
    """Response after starting plant tracking"""
    instance_id: int = Field(..., description="Created plant instance ID")
    plant_nickname: str = Field(..., description="Plant's nickname")
    start_date: date = Field(..., description="Start date")
    expected_maturity_date: date = Field(..., description="Expected maturity date")
    current_stage: str = Field(..., description="Current growth stage")
    message: str = Field(..., description="Success message")


class PlantInstanceSummary(BaseModel):
    """Summary of a user's plant instance"""
    instance_id: int = Field(..., description="Plant instance ID")
    plant_id: int = Field(..., description="Plant ID")
    plant_name: str = Field(..., description="Plant name")
    plant_nickname: str = Field(..., description="User's nickname for this plant")
    start_date: date = Field(..., description="Start date")
    expected_maturity_date: date = Field(..., description="Expected maturity date")
    current_stage: str = Field(..., description="Current growth stage")
    days_elapsed: int = Field(..., description="Days since start")
    progress_percentage: float = Field(..., description="Overall progress percentage")
    location_details: Optional[str] = Field(None, description="Location details")
    image_url: Optional[str] = Field(None, description="Plant image URL")


class PaginationInfo(BaseModel):
    """Pagination information"""
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")


class UserPlantsResponse(BaseModel):
    """Response with user's plant instances"""
    plants: List[PlantInstanceSummary] = Field(..., description="List of plant instances")
    total_count: int = Field(..., description="Total number of plants")
    active_count: int = Field(..., description="Number of active plants")
    pagination: PaginationInfo = Field(..., description="Pagination info")


class PlantDetails(BaseModel):
    """Plant details"""
    plant_id: int = Field(..., description="Plant ID")
    plant_name: str = Field(..., description="Plant name")
    scientific_name: Optional[str] = Field(None, description="Scientific name")
    plant_category: Optional[str] = Field(None, description="Plant category")


class TrackingInfo(BaseModel):
    """Tracking information for a plant instance"""
    plant_nickname: str = Field(..., description="Plant nickname")
    start_date: date = Field(..., description="Start date")
    expected_maturity_date: date = Field(..., description="Expected maturity date")
    current_stage: str = Field(..., description="Current growth stage")
    days_elapsed: int = Field(..., description="Days since start")
    progress_percentage: float = Field(..., description="Progress percentage")
    is_active: bool = Field(..., description="Whether plant is active")
    user_notes: Optional[str] = Field(None, description="User's notes")
    location_details: Optional[str] = Field(None, description="Location details")


class TimelineStage(BaseModel):
    """Timeline stage with completion status"""
    stage_name: str = Field(..., description="Stage name")
    start_day: int = Field(..., description="Start day")
    end_day: int = Field(..., description="End day")
    description: str = Field(..., description="Description")
    is_completed: bool = Field(..., description="Whether stage is completed")
    is_current: bool = Field(default=False, description="Whether this is current stage")
    key_indicators: List[str] = Field(..., description="Key indicators")


class Timeline(BaseModel):
    """Timeline information"""
    stages: List[TimelineStage] = Field(..., description="Growth stages with status")


class PlantInstanceDetailResponse(BaseModel):
    """Detailed response for a specific plant instance"""
    instance_id: int = Field(..., description="Instance ID")
    plant_details: PlantDetails = Field(..., description="Plant details")
    tracking_info: TrackingInfo = Field(..., description="Tracking information")
    timeline: Timeline = Field(..., description="Timeline with stages")
    current_tips: List[str] = Field(..., description="Current stage tips")


class RequirementsResponse(BaseModel):
    """Response with requirements checklist"""
    plant_id: int = Field(..., description="Plant ID")
    requirements: List[RequirementCategory] = Field(..., description="Requirements by category")


class InstructionsResponse(BaseModel):
    """Response with setup instructions"""
    plant_id: int = Field(..., description="Plant ID")
    instructions: List[SetupInstruction] = Field(..., description="Setup instructions")


class TimelineResponse(BaseModel):
    """Response with growth timeline"""
    plant_id: int = Field(..., description="Plant ID")
    total_days: int = Field(..., description="Total days to maturity")
    stages: List[GrowthStage] = Field(..., description="Growth stages")


class StageInfo(BaseModel):
    """Information about current stage"""
    stage_name: str = Field(..., description="Stage name")
    description: str = Field(..., description="Stage description")
    days_in_stage: int = Field(..., description="Days spent in this stage")
    estimated_days_remaining: int = Field(..., description="Estimated days remaining in stage")


class TipsResponse(BaseModel):
    """Response with current stage tips"""
    instance_id: int = Field(..., description="Instance ID")
    current_stage: str = Field(..., description="Current stage")
    tips: List[CareTip] = Field(..., description="Tips for current stage")
    stage_info: StageInfo = Field(..., description="Current stage information")


class ProgressSummary(BaseModel):
    """Progress summary for checklist"""
    completed_items: int = Field(..., description="Number of completed items")
    total_items: int = Field(..., description="Total number of items")
    completion_percentage: float = Field(..., description="Completion percentage")


class ChecklistCompleteResponse(BaseModel):
    """Response after marking checklist item complete"""
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Status message")
    progress_summary: ProgressSummary = Field(..., description="Updated progress summary")


class MessageResponse(BaseModel):
    """Generic message response"""
    success: bool = Field(..., description="Whether operation was successful")
    message: str = Field(..., description="Response message")


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Error response wrapper"""
    error: ErrorDetail = Field(..., description="Error information")


# ============================================================================
# CHAT SCHEMAS (Iteration 3 - Session 3)
# ============================================================================

class StartChatRequest(BaseModel):
    """Request to start a chat session"""
    user_id: int = Field(..., description="User ID")


class ChatMessageRequest(BaseModel):
    """Request to send a message in a chat"""
    chat_id: int = Field(..., description="Chat session ID")
    message: str = Field(..., description="Message text content")
    image: Optional[str] = Field(None, description="Optional base64-encoded image")


class ChatMessageResponse(BaseModel):
    """Response after sending a chat message"""
    chat_id: int = Field(..., description="Chat session ID")
    user_message: str = Field(..., description="User's message")
    ai_response: str = Field(..., description="AI assistant's response")
    tokens_used: int = Field(..., description="Tokens used for this exchange")
    total_tokens: int = Field(..., description="Total tokens used in conversation")
    token_warning: bool = Field(..., description="Whether approaching token limit")
    message: Optional[str] = Field(None, description="Warning message if applicable")


class ChatHistoryMessage(BaseModel):
    """Individual message in chat history"""
    id: int = Field(..., description="Message ID")
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    has_image: bool = Field(..., description="Whether message included an image")
    created_at: str = Field(..., description="Message creation timestamp")


class ChatHistoryResponse(BaseModel):
    """Response with full chat history"""
    chat_id: int = Field(..., description="Chat session ID")
    chat_type: str = Field(..., description="Chat type (general or plant_specific)")
    created_at: str = Field(..., description="Chat creation timestamp")
    expires_at: str = Field(..., description="Chat expiration timestamp")
    total_tokens: int = Field(..., description="Total tokens used in conversation")
    message_count: int = Field(..., description="Number of messages exchanged")
    is_active: bool = Field(..., description="Whether chat is active")
    messages: List[ChatHistoryMessage] = Field(..., description="List of messages")


class StartChatResponse(BaseModel):
    """Response after starting a chat session"""
    chat_id: int = Field(..., description="Created chat session ID")
    chat_type: str = Field(..., description="Chat type (general or plant_specific)")
    instance_id: Optional[int] = Field(None, description="Plant instance ID if plant-specific")
    plant_name: Optional[str] = Field(None, description="Plant name if plant-specific")
    plant_nickname: Optional[str] = Field(None, description="Plant nickname if plant-specific")
    expires_at: str = Field(..., description="Chat expiration timestamp")
    message: str = Field(..., description="Welcome message")


class EndChatResponse(BaseModel):
    """Response after ending a chat session"""
    success: bool = Field(..., description="Whether chat was ended successfully")
    message: str = Field(..., description="Status message")
    chat_id: int = Field(..., description="Chat session ID that was ended")
