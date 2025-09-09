# Plantopia Backend Architecture

## Overview

The Plantopia backend has been reorganized into a clean, layered architecture following FastAPI best practices. This structure promotes separation of concerns, testability, and maintainability, while preparing for AWS deployment.

## Directory Structure

```
backend/Plantopia/
├── app/                          # Main application package
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   └── endpoints.py         # All API endpoints
│   ├── core/                    # Core configuration
│   │   ├── __init__.py
│   │   └── config.py            # Application settings
│   ├── models/                  # Data models
│   │   ├── __init__.py
│   │   └── plant.py             # Plant data model
│   ├── schemas/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── request.py           # Request schemas
│   │   └── response.py          # Response schemas
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── plant_service.py     # Plant-related logic
│   │   ├── recommendation_service.py # Recommendation logic
│   │   └── google_drive_service.py   # Google Drive integration
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   └── plant_repository.py  # Plant data access
│   ├── recommender/             # Recommendation engine (moved from root)
│   │   ├── __init__.py
│   │   ├── engine.py            # Core recommendation logic
│   │   ├── normalization.py    # Data normalization
│   │   └── scoring.py           # Scoring algorithms
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   └── image_utils.py       # Image processing utilities
│   ├── __init__.py
│   └── main.py                  # FastAPI application entry point
├── data/                        # All data files
│   ├── csv/                     # CSV data files
│   │   ├── flower_plants_data.csv
│   │   ├── herbs_plants_data.csv
│   │   └── vegetable_plants_data.csv
│   └── json/                    # JSON configuration files
│       ├── climate_data.json
│       ├── user_preferences.json
│       └── test_victoria_images.json
├── tests/                       # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── fixtures/                # Test fixtures and data
│   └── legacy/                  # Legacy test files
├── docs/                        # Documentation
│   ├── README_ARCHITECTURE.md   # This file
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── DEBUG_GUIDE.md
│   └── ...                     # Other documentation
├── scripts/                     # Utility scripts
│   └── show_vercel_env_vars.sh
├── archive/                     # Deprecated/old files
│   ├── api.py                   # Old FastAPI implementation
│   ├── api_working.py           # Working API version
│   ├── vercel.json              # Vercel configuration (no longer needed)
│   ├── main.py                  # Old CLI tool
│   └── api/                     # Vercel serverless functions
├── frontend/                    # Frontend (to be moved to separate repo)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── .gitignore
└── README.md                    # Project README
```

## Architecture Layers

### 1. API Layer (`app/api/`)
- **Purpose**: Handle HTTP requests and responses
- **Components**:
  - `endpoints.py`: All API endpoints with proper routing
- **Responsibilities**:
  - Request validation
  - Response formatting
  - HTTP status codes
  - API documentation

### 2. Schema Layer (`app/schemas/`)
- **Purpose**: Define data contracts for API
- **Components**:
  - `request.py`: Input validation schemas
  - `response.py`: Output formatting schemas
- **Responsibilities**:
  - Data validation
  - Serialization/deserialization
  - API documentation generation

### 3. Service Layer (`app/services/`)
- **Purpose**: Implement business logic
- **Components**:
  - `plant_service.py`: Plant management logic
  - `recommendation_service.py`: Recommendation algorithm orchestration
- **Responsibilities**:
  - Business rules implementation
  - Orchestration of multiple repositories
  - Data transformation
  - External service integration

### 4. Repository Layer (`app/repositories/`)
- **Purpose**: Handle data access
- **Components**:
  - `plant_repository.py`: Plant data access from CSV files
- **Responsibilities**:
  - Data retrieval
  - Data caching
  - File system operations
  - Database operations (future)

### 5. Model Layer (`app/models/`)
- **Purpose**: Define domain entities
- **Components**:
  - `plant.py`: Plant entity model
- **Responsibilities**:
  - Data structure definition
  - Business entity behavior
  - Data conversion methods

### 6. Core Layer (`app/core/`)
- **Purpose**: Application configuration and setup
- **Components**:
  - `config.py`: Centralized configuration
- **Responsibilities**:
  - Environment configuration
  - Application settings
  - Constants definition

### 7. Utils Layer (`app/utils/`)
- **Purpose**: Shared utility functions
- **Components**:
  - `image_utils.py`: Image processing utilities
- **Responsibilities**:
  - Common helper functions
  - Cross-cutting concerns
  - Reusable utilities

## Data Flow

1. **Request Flow**:
   ```
   Client Request → API Endpoint → Service Layer → Repository Layer → Data Source
   ```

2. **Response Flow**:
   ```
   Data Source → Repository Layer → Service Layer → API Endpoint → Client Response
   ```

## Key Design Patterns

### Dependency Injection
- Services are injected into endpoints using FastAPI's dependency injection
- Repositories are injected into services
- Promotes testability and loose coupling

### Repository Pattern
- Abstracts data access logic
- Makes it easy to switch data sources (CSV → Database)
- Centralizes query logic

### Service Layer Pattern
- Encapsulates business logic
- Coordinates between multiple repositories
- Keeps endpoints thin and focused

### DTO Pattern (Data Transfer Objects)
- Pydantic schemas act as DTOs
- Separate internal models from API contracts
- Provides validation and documentation

## Running the Application

### Using the new structure:
```bash
# Run with uvicorn
uvicorn app.main:app --reload

# Or run directly
python -m app.main
```

### API Endpoints

All endpoints are now versioned under `/api/v1`:

- `GET /` - Root health check
- `GET /api/v1/` - API health check
- `POST /api/v1/recommendations` - Get plant recommendations
- `GET /api/v1/plants` - Get all plants
- `POST /api/v1/plant-score` - Score a specific plant

## Recent Restructuring (Updated)

### Changes Made
1. **Organized File Structure**:
   - Moved all CSV data files to `data/csv/`
   - Moved all JSON configuration files to `data/json/`
   - Relocated `recommender/` module to `app/recommender/`
   - Archived old API implementations in `archive/`
   - Organized tests into `tests/` with proper subdirectories
   - Consolidated documentation in `docs/`

2. **Updated Import Paths**:
   - All imports now use `app.recommender` instead of `recommender`
   - Configuration paths updated to reference new data locations
   - Test files updated with correct relative paths

3. **Prepared for AWS Deployment**:
   - Removed Vercel-specific configurations
   - Clean separation between application and infrastructure
   - Ready for containerization and AWS services integration

### Migration Notes

#### For Frontend Integration
Update API calls to use the new versioned endpoints:
```javascript
// Old
fetch('http://localhost:8000/recommendations')

// New
fetch('http://localhost:8000/api/v1/recommendations')
```

#### Import Path Updates
```python
# Old
from recommender.engine import load_all_plants
from recommender.scoring import calculate_scores

# New
from app.recommender.engine import load_all_plants
from app.recommender.scoring import calculate_scores
```

#### Data File Paths
```python
# Old
csv_paths = {
    "flower": "flower_plants_data.csv",
    "herb": "herbs_plants_data.csv",
    "vegetable": "vegetable_plants_data.csv"
}

# New (configured in app/core/config.py)
csv_paths = {
    "flower": "data/csv/flower_plants_data.csv",
    "herb": "data/csv/herbs_plants_data.csv",
    "vegetable": "data/csv/vegetable_plants_data.csv"
}
```

## AWS Deployment Preparation

### Next Steps for AWS Migration

1. **Containerization** (Required):
   ```dockerfile
   # Dockerfile needed
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **AWS Services to Configure**:
   - **ECS/Fargate**: For container orchestration
   - **ECR**: For Docker image registry
   - **ALB**: For load balancing
   - **RDS**: For database (optional, currently using CSV)
   - **S3**: For static file storage
   - **CloudWatch**: For logging and monitoring

3. **Required Configuration Files**:
   - `buildspec.yml`: For AWS CodeBuild
   - `appspec.yml`: For AWS CodeDeploy
   - `task-definition.json`: For ECS task definition
   - CloudFormation or Terraform templates

4. **Environment Variables**:
   - Move from `.env.example` to AWS Systems Manager Parameter Store
   - Configure secrets in AWS Secrets Manager

## Future Improvements

1. **Database Integration**:
   - Replace CSV files with AWS RDS (PostgreSQL)
   - Update repository layer to use SQLAlchemy ORM
   - Implement database migrations with Alembic

2. **Caching**:
   - Implement AWS ElastiCache (Redis) for frequently accessed data
   - Add caching decorators to service methods

3. **Authentication**:
   - Add AWS Cognito integration
   - Implement JWT authentication
   - Add API key management with AWS API Gateway

4. **Testing**:
   - Add unit tests for each layer
   - Implement integration tests
   - Add test fixtures and factories
   - Set up CI/CD with GitHub Actions and AWS CodePipeline

5. **Monitoring**:
   - Integrate with AWS CloudWatch for logging
   - Implement AWS X-Ray for distributed tracing
   - Add custom metrics and alarms

6. **Documentation**:
   - Generate OpenAPI documentation
   - Add AWS architecture diagrams
   - Create deployment guides

## Development Guidelines

1. **Adding New Endpoints**:
   - Define request/response schemas in `schemas/`
   - Implement business logic in `services/`
   - Add endpoint in `api/endpoints.py`

2. **Adding New Data Sources**:
   - Create repository in `repositories/`
   - Inject repository into relevant services
   - Update configuration if needed

3. **Code Style**:
   - Follow PEP 8 guidelines
   - Use type hints throughout
   - Document all public methods
   - Keep functions small and focused

4. **Error Handling**:
   - Use appropriate HTTP status codes
   - Provide meaningful error messages
   - Log errors for debugging
   - Handle exceptions at appropriate levels