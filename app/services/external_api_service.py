"""
External API Service for Gemini Integration (Iteration 3)
Handles all interactions with Gemini 2.5 Flash-Lite API for generating plant tracking data
"""
import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import google.generativeai as genai
from google.generativeai.types import GenerationConfig


logger = logging.getLogger(__name__)


class GeminiAPIService:
    """
    Service for interacting with Gemini API to generate plant tracking data.
    Implements API key rotation, rate limiting, and retry logic.
    """

    def __init__(self):
        """Initialize the Gemini API service with key management"""
        self.api_keys: List[Dict[str, str]] = []
        self.current_key_index: int = 0
        self.key_usage: Dict[str, Dict] = {}  # Track usage per key
        self.model_name: str = "gemini-2.5-flash-lite"
        self._load_api_keys()
        self._initialize_usage_tracking()

    def _load_api_keys(self) -> None:
        """Load API keys from gemini_api_keys.txt file"""
        try:
            api_keys_file = Path(__file__).parent.parent.parent / "gemini_api_keys.txt"

            if not api_keys_file.exists():
                logger.error(f"API keys file not found: {api_keys_file}")
                raise FileNotFoundError(f"gemini_api_keys.txt not found at {api_keys_file}")

            with open(api_keys_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):  # Skip empty lines and comments
                        parts = line.split(',')
                        if len(parts) == 2:
                            user, key = parts
                            self.api_keys.append({
                                'user': user.strip(),
                                'key': key.strip()
                            })

            if not self.api_keys:
                raise ValueError("No API keys found in gemini_api_keys.txt")

            logger.info(f"Loaded {len(self.api_keys)} API keys for Gemini")

        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            raise

    def _initialize_usage_tracking(self) -> None:
        """Initialize usage tracking for all API keys"""
        for key_info in self.api_keys:
            key_id = key_info['user']
            self.key_usage[key_id] = {
                'requests_today': 0,
                'tokens_today': 0,
                'last_request': None,
                'recent_requests': [],  # Last 60 seconds
                'last_reset': datetime.now().date()
            }

    def _get_current_key(self) -> str:
        """Get the current API key"""
        return self.api_keys[self.current_key_index]['key']

    def _get_current_key_id(self) -> str:
        """Get the current API key identifier"""
        return self.api_keys[self.current_key_index]['user']

    def _rotate_key(self) -> None:
        """Rotate to the next API key"""
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"Rotated to API key: {self._get_current_key_id()}")

    def _reset_daily_usage_if_needed(self, key_id: str) -> None:
        """Reset daily usage counters if it's a new day"""
        today = datetime.now().date()
        if self.key_usage[key_id]['last_reset'] != today:
            self.key_usage[key_id]['requests_today'] = 0
            self.key_usage[key_id]['tokens_today'] = 0
            self.key_usage[key_id]['last_reset'] = today
            logger.info(f"Reset daily usage for key: {key_id}")

    def _can_use_key(self, key_id: str) -> bool:
        """
        Check if key can be used without hitting rate limits.
        Rate limits: 15 req/min, 250K tokens/min, 1000 req/day
        """
        self._reset_daily_usage_if_needed(key_id)
        usage = self.key_usage[key_id]

        # Check daily request limit
        if usage['requests_today'] >= 1000:
            logger.warning(f"Key {key_id} hit daily request limit (1000)")
            return False

        # Check daily token limit (conservative estimate)
        if usage['tokens_today'] >= 250000:
            logger.warning(f"Key {key_id} hit daily token limit (250K)")
            return False

        # Check per-minute request limit
        now = datetime.now()
        one_minute_ago = now - timedelta(seconds=60)

        # Clean up old requests
        usage['recent_requests'] = [
            req_time for req_time in usage['recent_requests']
            if req_time > one_minute_ago
        ]

        if len(usage['recent_requests']) >= 15:
            logger.warning(f"Key {key_id} hit per-minute request limit (15)")
            return False

        return True

    def _track_api_usage(self, key_id: str, tokens_used: int = 0) -> None:
        """Track API usage for rate limiting"""
        now = datetime.now()
        usage = self.key_usage[key_id]

        usage['requests_today'] += 1
        usage['tokens_today'] += tokens_used
        usage['last_request'] = now
        usage['recent_requests'].append(now)

        logger.debug(f"Key {key_id} usage: {usage['requests_today']} requests, {usage['tokens_today']} tokens today")

    def _find_available_key(self) -> Optional[str]:
        """Find an available API key that hasn't hit rate limits"""
        start_index = self.current_key_index

        for _ in range(len(self.api_keys)):
            key_id = self._get_current_key_id()
            if self._can_use_key(key_id):
                return self._get_current_key()
            self._rotate_key()

        # Return to original key
        self.current_key_index = start_index
        return None

    async def _make_api_call_with_retry(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make API call with automatic retries and exponential backoff.

        Args:
            prompt: The prompt to send to Gemini
            system_instruction: System instruction for the AI
            response_schema: JSON schema for structured output
            max_retries: Maximum number of retry attempts

        Returns:
            Parsed JSON response from Gemini
        """
        for attempt in range(max_retries):
            try:
                # Find an available API key
                api_key = self._find_available_key()
                if not api_key:
                    wait_time = 60  # Wait 1 minute if all keys are rate limited
                    logger.warning(f"All API keys rate limited. Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    api_key = self._find_available_key()

                    if not api_key:
                        raise Exception("All API keys exhausted. Cannot make request.")

                # Configure Gemini with current API key
                genai.configure(api_key=api_key)
                key_id = self._get_current_key_id()

                # Create model with generation config
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=response_schema
                    ),
                    system_instruction=system_instruction
                )

                # Make the API call
                logger.info(f"Making Gemini API call (attempt {attempt + 1}/{max_retries}) with key: {key_id}")
                response = await asyncio.to_thread(
                    model.generate_content,
                    prompt
                )

                # Track usage (estimate tokens)
                estimated_tokens = len(prompt.split()) + len(response.text.split())
                self._track_api_usage(key_id, estimated_tokens)

                # Parse and return response
                import json
                result = json.loads(response.text)
                logger.info(f"Gemini API call successful with key: {key_id}")
                return result

            except Exception as e:
                logger.error(f"Gemini API call failed (attempt {attempt + 1}/{max_retries}): {e}")

                if attempt == max_retries - 1:
                    raise Exception(f"Gemini API call failed after {max_retries} attempts: {e}")

                # Exponential backoff
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)

                # Try next key on error
                self._rotate_key()

    def _build_plant_context(
        self,
        plant_data: Dict[str, Any],
        user_data: Dict[str, Any],
        location_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build rich context string from plant, user, and location data for API requests.

        Args:
            plant_data: Dictionary with plant information
            user_data: Dictionary with user preferences
            location_data: Optional dictionary with suburb and climate information

        Returns:
            Formatted context string
        """
        context_parts = [
            "PLANT INFORMATION:",
            f"- Name: {plant_data.get('plant_name', 'Unknown')}",
            f"- Scientific Name: {plant_data.get('scientific_name', 'N/A')}",
            f"- Category: {plant_data.get('plant_category', 'N/A')}",
            f"- Description: {plant_data.get('description', 'N/A')}",
            f"- Water Requirements: {plant_data.get('water_requirements', 'N/A')}",
            f"- Sunlight Requirements: {plant_data.get('sunlight_requirements', 'N/A')}",
            f"- Soil Type: {plant_data.get('soil_type', 'N/A')}",
            f"- Time to Maturity: {plant_data.get('time_to_maturity_days', 'N/A')} days",
            f"- Maintenance Level: {plant_data.get('maintenance_level', 'N/A')}",
            f"- Climate Zone: {plant_data.get('climate_zone', 'N/A')}",
            f"- Plant Spacing: {plant_data.get('plant_spacing', 'N/A')}",
            f"- Sowing Depth: {plant_data.get('sowing_depth', 'N/A')}",
            f"- Germination: {plant_data.get('germination', 'N/A')}",
            f"- Hardiness: {plant_data.get('hardiness_life_cycle', 'N/A')}",
            f"- Characteristics: {plant_data.get('characteristics', 'N/A')}",
            f"- Care Instructions: {plant_data.get('care_instructions', 'N/A')}",
            "",
            "USER CONTEXT:",
            f"- Experience Level: {user_data.get('experience_level', 'beginner')}",
            f"- Garden Type: {user_data.get('garden_type', 'backyard')}",
            f"- Available Space: {user_data.get('available_space_m2', user_data.get('available_space', 10.0))}m²",
            f"- Climate Goal: {user_data.get('climate_goal', 'general gardening')}"
        ]

        # Add location and climate data if available
        if location_data:
            context_parts.extend([
                "",
                "LOCATION & CLIMATE:",
                f"- Location: {location_data.get('location', 'N/A')}",
                f"- Climate Zone: {location_data.get('climate_zone', 'N/A')}",
                f"- Urban Heat Category: {location_data.get('heat_category', 'N/A')}",
                f"- Current Temperature: {location_data.get('temperature', 'N/A')}°C",
                f"- Humidity: {location_data.get('humidity', 'N/A')}%",
                f"- UV Index: {location_data.get('uv_index', 'N/A')} ({location_data.get('uv_category', 'N/A')})",
                f"- Air Quality: {location_data.get('aqi', 'N/A')} ({location_data.get('aqi_category', 'N/A')})"
            ])

        return "\n".join(context_parts)

    async def generate_requirements(
        self,
        plant_data: Dict[str, Any],
        user_data: Dict[str, Any],
        location_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate requirements checklist for a plant.

        Args:
            plant_data: Plant information
            user_data: User preferences
            location_data: Optional location and climate information

        Returns:
            Dictionary with requirements array
        """
        context = self._build_plant_context(plant_data, user_data, location_data)

        system_instruction = (
            "You are a professional horticulturist and gardening expert. Generate a comprehensive "
            "requirements checklist for growing the specified plant. Focus on practical, actionable "
            "items that a home gardener would need. Organize by categories and specify quantities "
            "where helpful. Consider the user's experience level and garden type."
        )

        prompt = f"{context}\n\nProvide a detailed checklist organized by categories."

        response_schema = {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "category": {"type": "string"},
                            "items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item": {"type": "string"},
                                        "quantity": {"type": "string"},
                                        "optional": {"type": "boolean"},
                                        "notes": {"type": "string"}
                                    },
                                    "required": ["item", "quantity", "optional"]
                                }
                            }
                        },
                        "required": ["category", "items"]
                    }
                }
            },
            "required": ["requirements"]
        }

        return await self._make_api_call_with_retry(prompt, system_instruction, response_schema)

    async def generate_instructions(
        self,
        plant_data: Dict[str, Any],
        user_data: Dict[str, Any],
        location_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate step-by-step setup instructions for a plant.

        Args:
            plant_data: Plant information
            user_data: User preferences
            location_data: Optional location and climate information

        Returns:
            Dictionary with instructions array
        """
        context = self._build_plant_context(plant_data, user_data, location_data)

        system_instruction = (
            "You are a professional horticulturist providing detailed growing instructions. "
            "Create clear, sequential steps for setting up and initially growing the specified plant. "
            "Include timing, techniques, and helpful tips for each step. Tailor instructions to the "
            "user's experience level and garden setup."
        )

        prompt = f"{context}\n\nProvide step-by-step instructions from seed preparation through initial growth phase."

        response_schema = {
            "type": "object",
            "properties": {
                "instructions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "step": {"type": "integer"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "duration": {"type": "string"},
                            "tips": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "warnings": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["step", "title", "description", "duration", "tips"]
                    }
                }
            },
            "required": ["instructions"]
        }

        return await self._make_api_call_with_retry(prompt, system_instruction, response_schema)

    async def generate_timeline(
        self,
        plant_data: Dict[str, Any],
        user_data: Dict[str, Any],
        location_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate growth timeline and care tips for a plant.

        Args:
            plant_data: Plant information
            user_data: User preferences
            location_data: Optional location and climate information

        Returns:
            Dictionary with growth_stages and care_tips arrays
        """
        context = self._build_plant_context(plant_data, user_data, location_data)

        system_instruction = (
            "You are a professional horticulturist creating a comprehensive growth timeline and care guide. "
            "Define specific growth stages with timing, key indicators, and stage-specific care tips. "
            "Base timeline on the plant's actual maturity period and provide practical, actionable advice "
            "for each stage. Provide 15-20 total care tips distributed across stages."
        )

        prompt = f"{context}\n\nCreate a detailed timeline with stages, key indicators, and 15-20 total care tips distributed across stages."

        response_schema = {
            "type": "object",
            "properties": {
                "growth_stages": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "stage_name": {"type": "string"},
                            "start_day": {"type": "integer"},
                            "end_day": {"type": "integer"},
                            "description": {"type": "string"},
                            "key_indicators": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "stage_order": {"type": "integer"}
                        },
                        "required": ["stage_name", "start_day", "end_day", "description", "key_indicators", "stage_order"]
                    }
                },
                "care_tips": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "stage_name": {"type": "string"},
                            "tips": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tip": {"type": "string"},
                                        "category": {"type": "string"},
                                        "importance": {"type": "string"}
                                    },
                                    "required": ["tip", "category", "importance"]
                                }
                            }
                        },
                        "required": ["stage_name", "tips"]
                    }
                }
            },
            "required": ["growth_stages", "care_tips"]
        }

        return await self._make_api_call_with_retry(prompt, system_instruction, response_schema)

    async def generate_complete_plant_data(
        self,
        plant_data: Dict[str, Any],
        user_data: Dict[str, Any],
        location_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate all plant tracking data (requirements, instructions, timeline) in parallel.

        Args:
            plant_data: Plant information
            user_data: User preferences
            location_data: Optional location and climate information

        Returns:
            Combined dictionary with all generated data
        """
        logger.info(f"Generating complete plant data for: {plant_data.get('plant_name')}")

        # Make all three API calls concurrently for efficiency
        requirements_task = self.generate_requirements(plant_data, user_data, location_data)
        instructions_task = self.generate_instructions(plant_data, user_data, location_data)
        timeline_task = self.generate_timeline(plant_data, user_data, location_data)

        requirements, instructions, timeline = await asyncio.gather(
            requirements_task,
            instructions_task,
            timeline_task
        )

        # Combine results
        combined_data = {
            "requirements_checklist": requirements["requirements"],
            "setup_instructions": instructions["instructions"],
            "growth_stages": timeline["growth_stages"],
            "care_tips": timeline["care_tips"],
            "data_source_info": {
                "model": self.model_name,
                "generated_at": datetime.utcnow().isoformat(),
                "api_version": "1.0"
            }
        }

        logger.info(f"Successfully generated complete plant data for: {plant_data.get('plant_name')}")
        return combined_data


# Singleton instance
_gemini_service_instance: Optional[GeminiAPIService] = None


def get_gemini_service() -> GeminiAPIService:
    """Get or create the singleton Gemini API service instance"""
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiAPIService()
    return _gemini_service_instance
