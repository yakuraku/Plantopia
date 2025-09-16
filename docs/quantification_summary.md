# Climate Action Quantification Feature - Technical Summary

## Overview

The Climate Action Quantification feature implements a comprehensive per-plant environmental impact assessment system for the Plantopia platform. This system quantifies the real-world climate benefits of individual plants, helping users make informed decisions about their gardening choices based on measurable environmental impact.

## Framework Specification

### Core Methodology: Per-Plant Quantification Framework

The quantification system follows a 8-step process to convert plant characteristics and site context into user-facing environmental metrics:

1. **Site Context Normalization** - Factors in location constraints and environmental conditions
2. **Plant Biophysics Derivation** - Calculates plant-specific biological characteristics
3. **Core Impact Indices** - Computes 8 fundamental environmental metrics
4. **Preference-Aware Weighting** - Applies user goal-based scoring weights
5. **UHI Integration** - Incorporates Urban Heat Island data for local relevance
6. **User Impact Conversion** - Transforms technical metrics to user-friendly units
7. **Community Impact Projection** - Estimates neighborhood-scale benefits
8. **Confidence Assessment** - Provides data quality and reliability indicators

### Site Context Factors

#### Area Factor (`A_site`)
- **Containers**: `sum(size_weights)` where small=0.6, medium=1.0, large=1.6, very_large=2.4
- **Ground planting**: `area_m² / (plant_spacing_cm/100)²`

#### Sun Factor (`F_sun`)
- **Exposure mapping**: full_sun=7h, part_sun=4h, bright_shade=2h, low_light=0.5h
- **Mismatch penalties**: 40% reduction if plant sun need doesn't match site exposure

#### Wind Factor (`F_wind`)
- **Wind exposure**: sheltered=0.9, moderate=1.0, windy=1.1
- **Effects**: Boosts evapotranspiration but increases plant stress

#### UHI Context (`C_uhi`)
- **Heat category scaling**: Low=0.8, Moderate=1.0, High=1.2, Very High=1.3
- **Priority weighting**: Hotter suburbs amplify cooling value importance

#### Seasonality Factor (`F_season`)
- **Timing match**: start_now + correct season = 1.0, off-season = 0.5

### Plant Biophysics

#### Leaf Area Index Proxy (`LAI_p`)
Base values by type:
- **Herbs/leafy**: 2.0
- **Flowers/groundcovers**: 1.5
- **Shrubs**: 2.5
- **Climbers**: 3.0
- **Small trees**: 3.5

Adjustments:
- **Lush/dense foliage**: +0.3
- **Compact/dwarf**: -0.3

#### Canopy Coverage (`A_can`)
- **Formula**: `k × (spacing_m²)` where k=0.75 (default)
- **Container limits**: small=0.03m², medium=0.06m², large=0.12m², very_large=0.2m²

#### Transpiration Class (`T_class`)
- **Low water plants**: 0.7
- **Medium water**: 1.0
- **High water/vegetables**: 1.3
- **Wind adjustment**: Multiply by F_wind
- **Preference alignment**: -30% penalty for watering preference mismatches

#### Growth Speed (`G_speed`)
- **Fast (<60 days)**: 1.2
- **Standard (60-120 days)**: 1.0
- **Slow (>120 days)**: 0.8

## Core Impact Indices (Raw Metrics)

### 1. Cooling Index (0-100)
**Formula**: `zscore(LAI_p × A_can × T_class × F_sun × F_season) × C_uhi`

**Conversion to User Metric**:
- **ΔT_nearby** (°C): `clamp(0.15 × CI / 10, 0.1, 2.0)`
- **Range**: 0.1°C - 2.0°C temperature reduction in 1-3m radius

### 2. Air Quality Index (0-100)
**Formula**: `zscore(leafiness + surface_roughness + aromatic_bonus + pollutant_tolerance) × F_sun`

**Conversion to User Metric**:
- **AQ Points**: `map(0-100 → 0-15 points)` local air quality improvement
- **Factors**: Leaf surface area, plant structure complexity, fragrant properties

### 3. CO₂ Uptake (kg/year)
**Formula**: `base_by_type × A_can × G_speed × F_sun`

**Base rates by type**:
- **Herbs**: 0.3-0.8 kg/year
- **Flowers**: 0.5-1.2 kg/year
- **Compact shrubs**: 1-5 kg/year

### 4. Water Cycling (L/week)
**Formula**: `7 × T_class × A_can × F_sun`

**Range**: 1-50 L/week processed through transpiration

### 5. Biodiversity/Pollinator Score (0-100)
**Factors**:
- **Flowers present**: +30 points
- **Fragrant**: +20 points
- **Native species**: +15 points
- **Attracts pollinators**: +25 points
- **Extended bloom**: +10 points

### 6. Edible Yield (g/week)
**Formula**: `type_baseline × G_speed × F_sun × (A_can / median_A_can)`

**Baselines**:
- **Leafy greens**: 80 g/week
- **Herbs**: 30 g/week
- **Fruiting**: 120 g/week
- **Root vegetables**: 60 g/week
- **Legumes**: 70 g/week

### 7. Water Need (L/week)
**Formula**: `class_table(plant_type, size) × season_multiplier × wind_multiplier`

**Adjustments**:
- **Drought tolerant**: ×0.6
- **Moisture loving**: ×1.4
- **Seasonal factor**: Current season multiplier
- **Wind exposure**: Increases water need

### 8. Maintenance Load (mins/week)
**Base times by maintenance level**:
- **Low maintenance**: 5 mins/week
- **Medium maintenance**: 12 mins/week
- **High maintenance**: 25 mins/week

**Additional factors**:
- **Pruning required**: +5 mins/week
- **Pest management**: +3 mins/week

## Preference-Aware Suitability Scoring

### Goal-Based Weighting Systems

#### Edible Goal
```
weights = {
  yield: 40%, cooling: 20%, air_quality: 10%,
  biodiversity: 10%, maintenance: -10%,
  water_need: -10%, risk: -10%
}
```

#### Ornamental Goal
```
weights = {
  cooling: 25%, air_quality: 20%, biodiversity: 25%,
  aesthetics: 20%, maintenance: -5%, water_need: -5%
}
```

#### Mixed Goal
```
weights = {
  yield: 25%, cooling: 25%, air_quality: 15%,
  biodiversity: 15%, maintenance: -10%, water_need: -10%
}
```

### Additional Micro-Weights
- **Color preferences**: Flower color matching
- **Fragrance**: Aromatic plant bonus
- **Time to results**: Quick vs patient preferences
- **Budget considerations**: Cost-effectiveness weighting

## User-Facing Impact Metrics

### Impact Tiers and Ranges

| Score Range | Temp. Reduction | Air Quality | CO₂ Absorption | Water Processing |
|-------------|-----------------|-------------|----------------|------------------|
| **81-100**  | 1.5-2.0°C      | +12-15 pts  | 40-50kg/yr     | 30-50L/week      |
| **61-80**   | 1.0-1.4°C      | +8-11 pts   | 25-39kg/yr     | 20-29L/week      |
| **41-60**   | 0.5-0.9°C      | +4-7 pts    | 10-24kg/yr     | 10-19L/week      |
| **21-40**   | 0.1-0.4°C      | +1-3 pts    | 5-9kg/yr       | 5-9L/week        |
| **0-20**    | Negligible     | Negligible  | <5kg/yr        | <5L/week         |

### Risk Assessment Levels

#### Low Risk
- **Criteria**: Non-toxic, no thorns/spines, low pollen
- **Badge**: Green "Low Risk"

#### Medium Risk
- **Criteria**: Some thorns, moderate pollen, requires care around children
- **Badge**: Yellow "Medium Risk"

#### High Risk
- **Criteria**: Toxic/poisonous plants, significant hazards
- **Badge**: Red "High Risk"

### Confidence Levels

#### High Confidence (85-100%)
- **Data**: Complete plant spacing, characteristics, position, maturity data
- **Reliability**: Minimal estimation required

#### Medium Confidence (70-84%)
- **Data**: Most plant data available, some estimation
- **Reliability**: Good accuracy expected

#### Low Confidence (50-69%)
- **Data**: Limited plant data, significant estimation required
- **Reliability**: Results may vary significantly

## Community Impact Modeling

### Household Adoption Scenarios
**Formula**: `individual_impact × adoption_rate × estimated_households`

**Example Calculation**:
- Individual cooling: 0.8°C
- Adoption rate: 5% (1 in 20 households)
- Estimated households: 1,000
- **Community impact**: `0.8 × 0.05 × 1,000 = 40°C total cooling effect`

**Projection Message**:
> "If adopted by 5% of Richmond households, could contribute ~0.04°C cooling effect community-wide"

## Backend Implementation

### Core Service: `QuantificationService`

**File**: `app/services/quantification_service.py`

**Key Methods**:
```python
def quantify_plant_impact(plant, site, preferences, suburb, plant_count) -> QuantifiedImpact
def _normalize_context(site, suburb, preferences) -> Dict[str, float]
def _derive_plant_biophysics(plant) -> Dict[str, float]
def _calculate_impact_indices(plant, biophysics, context) -> ImpactMetrics
def _calculate_suitability_score(metrics, preferences) -> SuitabilityScore
```

### API Endpoints

#### 1. `/api/v1/quantify-plant` (POST)
**Purpose**: Quantify climate impact for a specific plant

**Request Schema**:
```json
{
  "plant_name": "string",
  "suburb": "string",
  "plant_count": 1,
  "user_preferences": {
    "site": { "location_type", "area_m2", "sun_exposure", "wind_exposure", "containers", "container_sizes" },
    "preferences": { "goal", "maintainability", "watering", "time_to_results", "season_intent" }
  }
}
```

**Response Schema**:
```json
{
  "plant_name": "string",
  "quantified_impact": {
    "temperature_reduction_c": 0.8,
    "air_quality_points": 12,
    "co2_absorption_kg_year": 2.5,
    "water_processed_l_week": 15.0,
    "pollinator_support": "High",
    "edible_yield": "80g/week after day 45",
    "maintenance_time": "8mins/week",
    "water_requirement": "4.5L/week",
    "risk_badge": "low",
    "confidence_level": "High (87%)",
    "why_this_plant": "Selected for: excellent cooling effect, strong air purification",
    "community_impact_potential": "If adopted by 5% of Richmond households..."
  },
  "suitability_score": {
    "total_score": 84.2,
    "breakdown": { "cooling": 25.0, "yield": 20.0, "maintenance": -5.0 }
  }
}
```

#### 2. `/api/v1/batch-quantify` (POST)
**Purpose**: Bulk quantification for up to 20 plants
**Input**: Array of `PlantQuantificationRequest`
**Output**: Array of `PlantQuantificationResponse`

#### 3. `/api/v1/recommendations-with-impact` (POST)
**Purpose**: Enhanced recommendations with quantified impact
**Extends**: Standard `/recommendations` endpoint
**Additional**: Adds `quantified_impact` field to each recommendation

#### 4. `/api/v1/quantification-info` (GET)
**Purpose**: Framework methodology and documentation
**Returns**:
- Framework version and description
- Metric calculation details
- Confidence level explanations
- Known limitations and calibration notes

### Database Integration

**Models Used**:
- **Plant**: Source plant data (characteristics, spacing, maturity, etc.)
- **Suburb**: UHI data (heat category, vegetation percentage, location)

**Repository Dependencies**:
- `DatabasePlantRepository`: Plant data access
- `ClimateRepository`: Suburb and climate data access

### Error Handling

**Graceful Degradation**:
- Missing plant data: Use category defaults with reduced confidence
- Missing suburb data: Use regional defaults with notification
- Quantification failures: Fall back to standard recommendations
- Invalid inputs: Clear error messages with suggestions

### Performance Considerations

**Optimization Strategies**:
- **Caching**: Suburb data and plant biophysics calculations
- **Batch processing**: Vectorized calculations for multiple plants
- **Lazy loading**: Only quantify on-demand or when explicitly requested
- **Confidence thresholds**: Skip expensive calculations for low-confidence scenarios

## Calibration and Validation

### Calibration Process
1. **Benchmark Plants**: Use 10-20 well-documented common plants
2. **Field Measurements**: Collect real-world performance data
3. **Parameter Tuning**: Adjust constants based on observed vs predicted results
4. **Seasonal Validation**: Test across different growing seasons
5. **User Feedback**: Incorporate actual gardener experiences

### Known Limitations
- **Microclimate Variations**: Local conditions may differ significantly
- **Plant Variety Differences**: Cultivar-specific performance variations
- **Maintenance Skill Levels**: User experience affects actual outcomes
- **Climate Change**: Long-term projections may need adjustment
- **Urban Context**: Building shadows, pollution, and other urban factors

### Future Enhancements
- **Machine Learning Integration**: Improve predictions with usage data
- **Seasonal Modeling**: More sophisticated seasonal adjustment factors
- **Soil Quality Integration**: Account for soil conditions and amendments
- **Pest/Disease Modeling**: Include regional pest pressure factors
- **Carbon Footprint**: Full lifecycle assessment including transportation

## Technical Dependencies

### Python Packages
```python
# Core dependencies (already in project)
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Math and data processing
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
```

### Database Schema Extensions
No new tables required - uses existing:
- `plants` table for plant characteristics
- `suburbs` table for UHI data
- Extends existing API schemas with new response fields

### Integration Points
- **Recommendation Engine**: Enhances existing plant recommendations
- **Climate Repository**: Uses suburb heat island data
- **Plant Repository**: Accesses plant characteristics and spacing data
- **Image Service**: Maintains compatibility with existing plant media handling

## Testing Strategy

### Unit Tests
- **Biophysics Calculations**: Test LAI, canopy, transpiration calculations
- **Context Normalization**: Verify site factor calculations
- **Impact Conversion**: Test raw metric to user-facing conversion
- **Edge Cases**: Handle missing data, invalid inputs, extreme values

### Integration Tests
- **End-to-End Quantification**: Full plant quantification workflow
- **API Endpoints**: Request/response validation
- **Database Integration**: Plant and suburb data retrieval
- **Error Handling**: Graceful degradation scenarios

### Performance Tests
- **Single Plant**: Response time <200ms target
- **Batch Quantification**: 20 plants <2s target
- **Enhanced Recommendations**: 5 plants with impact <1s target
- **Concurrent Users**: Load testing for production scaling

This comprehensive framework provides scientifically-grounded, user-friendly climate impact quantification while maintaining system performance and reliability.