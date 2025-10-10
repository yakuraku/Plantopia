# External API Integration Guide

## Overview
This document outlines the integration strategy with external APIs for generating plant-specific tracking data, requirements, and care instructions.

## API Selection & Configuration

### Primary API: Gemini 2.5 Flash-Lite
**Model**: `gemini-2.5-flash-lite`
**Reason**: High request limits, fast response times, structured output support

**Rate Limits Per API Key**:
- 15 Requests per minute
- 250,000 tokens per minute
- 1,000 requests per day

### API Key Management
**File**: `gemini_api_keys.txt` (exclude this from git)
**Sample Format**:
```
user1,API_key_1
user2,API_key_2
user3,API_key_3
user4,API_key_4
```

**Key Rotation Strategy**:
- Use 4-5 API keys for better throughput
- Round-robin rotation across keys
- Automatic fallback if key hits rate limit
- Daily usage tracking per key

## API Call Strategy

### Three Separate API Calls
To maximize quality and manage complexity, we make three separate structured API calls:

1. **Requirements Generation**
2. **Instructions Generation**
3. **Timeline & Tips Generation**

### Request Structure
All requests use:
- **System Instructions** for role definition
- **Structured Output** in JSON format
- **Rich Plant Context** for accuracy

## API Call Implementations

### 1. Requirements Generation API Call

**Purpose**: Generate comprehensive checklist of materials and tools needed

**System Instruction**:
```
You are a professional horticulturist and gardening expert. Generate a comprehensive requirements checklist for growing the specified plant. Focus on practical, actionable items that a home gardener would need. Organize by categories and specify quantities where helpful. Consider the user's experience level and garden type.
```

**Request Payload**:
```json
{
  "contents": [{
    "parts": [{
      "text": "Generate requirements checklist for:\n\nPLANT INFORMATION:\n- Name: [plant_name]\n- Scientific Name: [scientific_name]\n- Category: [plant_category]\n- Description: [description]\n- Water Requirements: [water_requirements]\n- Sunlight Requirements: [sunlight_requirements]\n- Soil Type: [soil_type]\n- Time to Maturity: [time_to_maturity_days] days\n- Maintenance Level: [maintenance_level]\n- Climate Zone: [climate_zone]\n- Plant Spacing: [plant_spacing]\n- Sowing Depth: [sowing_depth]\n- Germination: [germination]\n- Hardiness: [hardiness_life_cycle]\n- Characteristics: [characteristics]\n- Care Instructions: [care_instructions]\n\nUSER CONTEXT:\n- Experience Level: [experience_level]\n- Garden Type: [garden_type]\n- Available Space: [available_space]m²\n- Climate Goal: [climate_goal]\n\nProvide a detailed checklist organized by categories."
    }]
  }],
  "generationConfig": {
    "response_mime_type": "application/json",
    "response_schema": {
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
  },
  "systemInstruction": {
    "parts": [{"text": "[System instruction from above]"}]
  }
}
```

**Expected Response**:
```json
{
  "requirements": [
    {
      "category": "Seeds & Plants",
      "items": [
        {
          "item": "Cherry tomato seeds",
          "quantity": "1 packet (20-30 seeds)",
          "optional": false,
          "notes": "Choose disease-resistant varieties for beginners"
        }
      ]
    },
    {
      "category": "Growing Medium",
      "items": [
        {
          "item": "High-quality potting mix",
          "quantity": "20L bag",
          "optional": false,
          "notes": "Well-draining mix with organic matter"
        },
        {
          "item": "Compost or aged manure",
          "quantity": "5L",
          "optional": true,
          "notes": "Improves soil nutrition"
        }
      ]
    }
  ]
}
```

### 2. Instructions Generation API Call

**Purpose**: Generate step-by-step setup instructions

**System Instruction**:
```
You are a professional horticulturist providing detailed growing instructions. Create clear, sequential steps for setting up and initially growing the specified plant. Include timing, techniques, and helpful tips for each step. Tailor instructions to the user's experience level and garden setup.
```

**Request Payload**:
```json
{
  "contents": [{
    "parts": [{
      "text": "Generate detailed setup instructions for:\n\n[PLANT CONTEXT - same as above]\n\nProvide step-by-step instructions from seed preparation through initial growth phase."
    }]
  }],
  "generationConfig": {
    "response_mime_type": "application/json",
    "response_schema": {
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
  }
}
```

### 3. Timeline & Tips Generation API Call

**Purpose**: Generate growth stages timeline and care tips

**System Instruction**:
```
You are a professional horticulturist creating a comprehensive growth timeline and care guide. Define specific growth stages with timing, key indicators, and stage-specific care tips. Base timeline on the plant's actual maturity period and provide practical, actionable advice for each stage.
```

**Request Payload**:
```json
{
  "contents": [{
    "parts": [{
      "text": "Generate growth timeline and care tips for:\n\n[PLANT CONTEXT - same as above]\n\nCreate a detailed timeline with stages, key indicators, and 15-20 total care tips distributed across stages."
    }]
  }],
  "generationConfig": {
    "response_mime_type": "application/json",
    "response_schema": {
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
  }
}
```

## Implementation Details

### Service Class Structure
```python
class ExternalAPIService:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.key_usage = {}  # Track daily usage per key

    async def generate_requirements(self, plant_data: dict, user_data: dict) -> dict:
        """Generate requirements checklist"""
        pass

    async def generate_instructions(self, plant_data: dict, user_data: dict) -> dict:
        """Generate setup instructions"""
        pass

    async def generate_timeline(self, plant_data: dict, user_data: dict) -> dict:
        """Generate growth timeline and tips"""
        pass
```

### Context Builder
```python
def build_plant_context(plant: PlantModel, user_data: dict) -> str:
    """Build rich context string for API requests"""
    context_fields = [
        f"Name: {plant.plant_name}",
        f"Scientific Name: {plant.scientific_name}",
        f"Category: {plant.plant_category}",
        f"Description: {plant.description}",
        f"Water Requirements: {plant.water_requirements}",
        f"Sunlight Requirements: {plant.sunlight_requirements}",
        f"Soil Type: {plant.soil_type}",
        f"Time to Maturity: {plant.time_to_maturity_days} days",
        f"Maintenance Level: {plant.maintenance_level}",
        f"Climate Zone: {plant.climate_zone}",
        f"Plant Spacing: {plant.plant_spacing}",
        f"Sowing Depth: {plant.sowing_depth}",
        f"Germination: {plant.germination}",
        f"Hardiness: {plant.hardiness_life_cycle}",
        f"Characteristics: {plant.characteristics}",
        f"Care Instructions: {plant.care_instructions}"
    ]

    user_context = [
        f"Experience Level: {user_data.get('experience_level')}",
        f"Garden Type: {user_data.get('garden_type')}",
        f"Available Space: {user_data.get('available_space')}m²",
        f"Climate Goal: {user_data.get('climate_goal')}"
    ]

    return "\n".join(context_fields + user_context)
```

### Error Handling & Retries
```python
async def make_api_call_with_retry(self, payload: dict, max_retries: int = 3) -> dict:
    """Make API call with automatic retries and key rotation"""
    for attempt in range(max_retries):
        try:
            # Try current API key
            response = await self._make_request(payload, self.get_current_key())

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limited
                self._rotate_key()
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                response.raise_for_status()

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

### Caching Strategy
```python
async def get_or_generate_plant_data(self, plant_id: int, user_data: dict) -> dict:
    """Get existing data or generate new data via API"""

    # Check if data exists and is current
    existing_data = await self.repository.get_plant_growth_data(plant_id)

    if existing_data and self._is_data_current(existing_data):
        return existing_data

    # Generate new data via API
    plant = await self.plant_repository.get_plant(plant_id)
    plant_context = self.build_plant_context(plant, user_data)

    # Make three API calls concurrently
    requirements_task = self.generate_requirements(plant_context, user_data)
    instructions_task = self.generate_instructions(plant_context, user_data)
    timeline_task = self.generate_timeline(plant_context, user_data)

    requirements, instructions, timeline = await asyncio.gather(
        requirements_task, instructions_task, timeline_task
    )

    # Combine and cache results
    combined_data = {
        "plant_id": plant_id,
        "requirements_checklist": requirements["requirements"],
        "setup_instructions": instructions["instructions"],
        "growth_stages": timeline["growth_stages"],
        "care_tips": timeline["care_tips"],
        "last_updated": datetime.utcnow(),
        "version": "1.0"
    }

    await self.repository.save_plant_growth_data(combined_data)
    return combined_data
```

## Rate Limiting & Monitoring

### Usage Tracking
```python
def track_api_usage(self, key_id: str, tokens_used: int):
    """Track daily usage per API key"""
    today = datetime.now().date()

    if key_id not in self.key_usage:
        self.key_usage[key_id] = {}

    if today not in self.key_usage[key_id]:
        self.key_usage[key_id][today] = {"requests": 0, "tokens": 0}

    self.key_usage[key_id][today]["requests"] += 1
    self.key_usage[key_id][today]["tokens"] += tokens_used
```

### Rate Limit Management
```python
def can_use_key(self, key_id: str) -> bool:
    """Check if key can be used without hitting limits"""
    today = datetime.now().date()

    if key_id not in self.key_usage or today not in self.key_usage[key_id]:
        return True

    usage = self.key_usage[key_id][today]

    # Check daily limits
    if usage["requests"] >= 1000:  # Daily request limit
        return False

    if usage["tokens"] >= 250000:  # Daily token limit
        return False

    # Check recent requests for minute limit
    recent_requests = self._count_recent_requests(key_id, minutes=1)
    if recent_requests >= 15:  # Per-minute limit
        return False

    return True
```

## Testing Strategy

### Mock Responses
Create mock responses for testing:
```python
MOCK_REQUIREMENTS = {
    "requirements": [
        {
            "category": "Seeds & Plants",
            "items": [
                {
                    "item": "Test plant seeds",
                    "quantity": "1 packet",
                    "optional": False,
                    "notes": "Test notes"
                }
            ]
        }
    ]
}
```

### Integration Tests
```python
async def test_full_api_integration():
    """Test complete API workflow"""
    service = ExternalAPIService()

    # Test with real plant data
    plant_data = await get_test_plant()
    user_data = get_test_user_data()

    # Generate all data
    data = await service.get_or_generate_plant_data(
        plant_data.id, user_data
    )

    # Validate structure
    assert "requirements_checklist" in data
    assert "setup_instructions" in data
    assert "growth_stages" in data
    assert "care_tips" in data

    # Validate content quality
    assert len(data["requirements_checklist"]) > 0
    assert len(data["growth_stages"]) >= 3  # Minimum stages
    assert len(data["care_tips"]) >= 10  # Minimum tips
```

## Security & Best Practices

### API Key Security
- Store keys in environment variables or secure vault
- Never commit keys to version control
- Rotate keys periodically
- Monitor for unusual usage patterns

### Input Validation
- Sanitize all plant data before sending to API
- Validate JSON schema of API responses
- Handle malformed responses gracefully

### Cost Management
- Monitor token usage across all keys
- Set up alerts for high usage
- Implement circuit breakers for failed requests
- Cache responses aggressively to minimize API calls

## Monitoring & Alerting

### Key Metrics
- API response times
- Success/failure rates per key
- Daily token consumption
- Cache hit ratios

### Alerts
- API key approaching daily limits
- High error rates from external API
- Unusually long response times
- Cache miss rates exceeding threshold

### Logging
```python
import structlog

logger = structlog.get_logger()

async def log_api_call(self, call_type: str, plant_id: int, response_time: float, success: bool):
    """Log API call metrics"""
    logger.info(
        "external_api_call",
        call_type=call_type,
        plant_id=plant_id,
        response_time_ms=response_time * 1000,
        success=success,
        api_key_id=self.current_key_index
    )
```