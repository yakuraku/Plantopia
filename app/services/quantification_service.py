"""
Climate Action Quantification Service
Implements the per-plant quantification framework as specified
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from app.schemas.request import SitePreferences, UserPreferences
from app.models.database import Plant, Suburb


@dataclass
class ImpactMetrics:
    """Raw impact metrics for a plant"""
    cooling_index: float
    air_quality_improvement: float
    co2_uptake_kg_year: float
    water_cycling_l_week: float
    biodiversity_score: float
    edible_yield_g_week: Optional[float]
    water_need_l_week: float
    maintenance_mins_week: float
    risk_level: str
    confidence_score: float


@dataclass
class QuantifiedImpact:
    """User-facing quantified impact metrics"""
    temperature_reduction_c: float
    air_quality_points: int
    co2_absorption_kg_year: float
    water_processed_l_week: float
    pollinator_support: str
    edible_yield: Optional[str]
    maintenance_time: str
    water_requirement: str
    risk_badge: str
    confidence_level: str
    why_this_plant: str
    community_impact_potential: Optional[str] = None


@dataclass
class SuitabilityScore:
    """Suitability score with breakdown"""
    total_score: float
    breakdown: Dict[str, float]


class QuantificationService:
    """Service for quantifying climate action impact of plants"""

    # Z-score normalization constants (calibrated values)
    LAI_MEAN = 2.5
    LAI_STD = 0.8
    CANOPY_MEAN = 0.8
    CANOPY_STD = 0.4

    def __init__(self):
        """Initialize the quantification service"""
        pass

    def quantify_plant_impact(
        self,
        plant: Plant,
        site: SitePreferences,
        preferences: UserPreferences,
        suburb: Suburb,
        plant_count: int = 1
    ) -> QuantifiedImpact:
        """
        Main quantification method for a single plant

        Args:
            plant: Plant data from database
            site: Site preferences and constraints
            preferences: User preferences
            suburb: Suburb data for UHI context
            plant_count: Number of plants being installed

        Returns:
            QuantifiedImpact with user-facing metrics
        """
        # 1. Normalize site context
        context = self._normalize_context(site, suburb, preferences)

        # 2. Derive plant biophysics
        biophysics = self._derive_plant_biophysics(plant)

        # 3. Calculate core impact indices
        metrics = self._calculate_impact_indices(plant, biophysics, context)

        # 4. Calculate suitability score
        suitability = self._calculate_suitability_score(metrics, preferences)

        # 5. Convert to user-facing impact
        impact = self._convert_to_user_impact(metrics, plant_count)

        # 6. Add community impact potential
        impact.community_impact_potential = self._calculate_community_impact(
            impact, suburb, plant_count
        )

        return impact

    def _normalize_context(
        self,
        site: SitePreferences,
        suburb: Suburb,
        preferences: UserPreferences
    ) -> Dict[str, float]:
        """Normalize site context factors"""

        # Area factor
        area_factor = self._calculate_area_factor(site)

        # Sun factor with mismatch penalty
        sun_factor = self._calculate_sun_factor(site.sun_exposure)

        # Wind factor
        wind_factor = self._calculate_wind_factor(site.wind_exposure)

        # UHI context factor
        uhi_factor = self._calculate_uhi_factor(suburb)

        # Season factor
        season_factor = self._calculate_season_factor(preferences.season_intent)

        return {
            'area_factor': area_factor,
            'sun_factor': sun_factor,
            'wind_factor': wind_factor,
            'uhi_factor': uhi_factor,
            'season_factor': season_factor
        }

    def _calculate_area_factor(self, site: SitePreferences) -> float:
        """Calculate area capacity factor"""
        if site.containers and site.container_sizes:
            size_weights = {
                'small': 0.6,
                'medium': 1.0,
                'large': 1.6,
                'very_large': 2.4
            }

            return sum(size_weights.get(size, 1.0) for size in site.container_sizes)

        # For ground planting, estimate max plants based on area
        return math.sqrt(site.area_m2 / 0.25)  # Assuming 50cm spacing average

    def _calculate_sun_factor(self, sun_exposure: str) -> float:
        """Calculate sun exposure factor"""
        sun_hours = {
            'full_sun': 7,
            'part_sun': 4,
            'bright_shade': 2,
            'low_light': 0.5
        }

        return sun_hours.get(sun_exposure, 4) / 7

    def _calculate_wind_factor(self, wind_exposure: str) -> float:
        """Calculate wind factor"""
        wind_factors = {
            'sheltered': 0.9,
            'moderate': 1.0,
            'windy': 1.1
        }

        return wind_factors.get(wind_exposure, 1.0)

    def _calculate_uhi_factor(self, suburb: Suburb) -> float:
        """Calculate UHI context factor"""
        if not suburb or not suburb.suburb_heat_category:
            return 1.0

        heat_categories = {
            'Low Heat': 0.8,
            'Moderate Heat': 1.0,
            'High Heat': 1.2,
            'Very High Heat': 1.3
        }

        return heat_categories.get(suburb.suburb_heat_category, 1.0)

    def _calculate_season_factor(self, season_intent: str) -> float:
        """Calculate season factor"""
        return 1.0 if season_intent == 'start_now' else 0.5

    def _derive_plant_biophysics(self, plant: Plant) -> Dict[str, float]:
        """Derive plant biophysics from plant data"""

        lai_proxy = self._calculate_lai_proxy(plant)
        canopy_area = self._calculate_canopy_area(plant)
        transpiration_class = self._calculate_transpiration_class(plant)
        growth_speed = self._calculate_growth_speed(plant)

        return {
            'lai_proxy': lai_proxy,
            'canopy_area': canopy_area,
            'transpiration_class': transpiration_class,
            'growth_speed': growth_speed
        }

    def _calculate_lai_proxy(self, plant: Plant) -> float:
        """Calculate Leaf Area Index proxy"""
        base_lai = {
            'herb': 2.0,
            'flower': 1.5,
            'vegetable': 2.2
        }

        lai = base_lai.get(plant.plant_category, 2.0)

        # Adjust based on characteristics
        if plant.characteristics:
            chars = plant.characteristics.lower()
            if 'lush' in chars or 'dense' in chars:
                lai += 0.3
            if 'compact' in chars or 'dwarf' in chars:
                lai -= 0.3

        return max(0.5, lai)

    def _calculate_canopy_area(self, plant: Plant) -> float:
        """Calculate canopy area per plant"""
        spacing_cm = self._extract_spacing(plant.plant_spacing)
        spacing_m = spacing_cm / 100

        return 0.75 * (spacing_m ** 2)  # k factor of 0.75

    def _extract_spacing(self, spacing_str: Optional[str]) -> float:
        """Extract spacing in cm from spacing string"""
        if not spacing_str:
            return 30.0  # default

        import re
        match = re.search(r'(\d+)', spacing_str)
        return float(match.group(1)) if match else 30.0

    def _calculate_transpiration_class(self, plant: Plant) -> float:
        """Calculate transpiration class"""
        if not plant.characteristics and not plant.position:
            return 1.0

        chars = (plant.characteristics or '').lower()
        position = (plant.position or '').lower()

        if 'drought' in chars or 'dry' in position:
            return 0.7
        elif 'moist' in chars or plant.plant_category == 'vegetable':
            return 1.3

        return 1.0

    def _calculate_growth_speed(self, plant: Plant) -> float:
        """Calculate growth speed factor"""
        if not plant.time_to_maturity_days:
            return 1.0

        if plant.time_to_maturity_days <= 60:
            return 1.2  # fast
        elif plant.time_to_maturity_days > 120:
            return 0.8  # slow

        return 1.0

    def _calculate_impact_indices(
        self,
        plant: Plant,
        biophysics: Dict[str, float],
        context: Dict[str, float]
    ) -> ImpactMetrics:
        """Calculate core impact indices"""

        lai = biophysics['lai_proxy']
        canopy = biophysics['canopy_area']
        transpiration = biophysics['transpiration_class']
        growth = biophysics['growth_speed']

        sun_factor = context['sun_factor']
        wind_factor = context['wind_factor']
        uhi_factor = context['uhi_factor']
        season_factor = context['season_factor']

        # 1. Cooling Index
        cooling_raw = lai * canopy * transpiration * sun_factor * season_factor
        cooling_index = self._zscore(cooling_raw, self.LAI_MEAN * self.CANOPY_MEAN,
                                   self.LAI_STD * self.CANOPY_STD) * uhi_factor

        # 2. Air Quality Index
        aqi_raw = lai + self._get_surface_roughness(plant) + self._get_aromatic_bonus(plant)
        air_quality_improvement = max(0, min(100, self._zscore(aqi_raw, 3.0, 1.0) * sun_factor))

        # 3. CO2 Uptake
        base_co2 = self._get_base_co2_by_type(plant.plant_category)
        co2_uptake_kg_year = base_co2 * canopy * growth * sun_factor

        # 4. Water Cycling
        water_cycling_l_week = 7 * transpiration * canopy * sun_factor

        # 5. Biodiversity Score
        biodiversity_score = self._calculate_biodiversity_score(plant)

        # 6. Edible Yield
        edible_yield_g_week = None
        if plant.plant_category in ['vegetable', 'herb']:
            edible_yield_g_week = self._calculate_edible_yield(plant, growth, sun_factor, canopy)

        # 7. Water Need
        water_need_l_week = self._calculate_water_need(plant, season_factor, wind_factor)

        # 8. Maintenance Load
        maintenance_mins_week = self._calculate_maintenance_load(plant)

        # 9. Risk Assessment
        risk_level = self._assess_risk(plant)

        # 10. Confidence Score
        confidence_score = self._calculate_confidence(plant)

        return ImpactMetrics(
            cooling_index=max(0, min(100, cooling_index)),
            air_quality_improvement=air_quality_improvement,
            co2_uptake_kg_year=co2_uptake_kg_year,
            water_cycling_l_week=water_cycling_l_week,
            biodiversity_score=biodiversity_score,
            edible_yield_g_week=edible_yield_g_week,
            water_need_l_week=water_need_l_week,
            maintenance_mins_week=maintenance_mins_week,
            risk_level=risk_level,
            confidence_score=confidence_score
        )

    def _zscore(self, value: float, mean: float, std: float) -> float:
        """Calculate z-score and scale to 0-100"""
        return ((value - mean) / std) * 10 + 50

    def _get_surface_roughness(self, plant: Plant) -> float:
        """Get surface roughness factor"""
        plant_type = (plant.plant_type or '').lower()
        if 'shrub' in plant_type or 'tree' in plant_type:
            return 1.5
        elif 'climbing' in plant_type or 'vine' in plant_type:
            return 1.2
        return 0.8

    def _get_aromatic_bonus(self, plant: Plant) -> float:
        """Get aromatic/fragrant bonus"""
        chars = (plant.characteristics or '').lower()
        return 0.5 if 'fragrant' in chars or 'aromatic' in chars else 0.0

    def _get_base_co2_by_type(self, category: str) -> float:
        """Get base CO2 absorption by plant type"""
        base_co2 = {
            'herb': 0.5,
            'flower': 0.8,
            'vegetable': 1.0
        }
        return base_co2.get(category, 0.8)

    def _calculate_biodiversity_score(self, plant: Plant) -> float:
        """Calculate biodiversity/pollinator score"""
        score = 30  # base score

        chars = (plant.characteristics or '').lower()
        category = plant.plant_category

        if category == 'flower':
            score += 30
        if 'fragrant' in chars:
            score += 20
        if 'attracts' in chars or 'pollinator' in chars:
            score += 25
        if 'native' in chars:
            score += 15

        return min(100, score)

    def _calculate_edible_yield(
        self,
        plant: Plant,
        growth_speed: float,
        sun_factor: float,
        canopy_area: float
    ) -> float:
        """Calculate edible yield in g/week"""
        type_baselines = {
            'herb': 30,
            'vegetable': 80
        }

        baseline = type_baselines.get(plant.plant_category, 0)
        return baseline * growth_speed * sun_factor * (canopy_area / 0.5)

    def _calculate_water_need(
        self,
        plant: Plant,
        season_factor: float,
        wind_factor: float
    ) -> float:
        """Calculate water need in L/week"""
        chars = (plant.characteristics or '').lower()
        category = plant.plant_category

        base_need = 3.0  # liters per week

        if 'drought' in chars:
            base_need *= 0.6
        elif 'moist' in chars or category == 'vegetable':
            base_need *= 1.4

        return base_need * season_factor * wind_factor

    def _calculate_maintenance_load(self, plant: Plant) -> float:
        """Calculate maintenance load in minutes/week"""
        chars = (plant.characteristics or '').lower()

        base_mins = 8.0

        if 'low maintenance' in chars or 'hardy' in chars:
            base_mins *= 0.7
        elif 'high maintenance' in chars:
            base_mins *= 1.8

        if 'pruning' in chars:
            base_mins += 5

        return round(base_mins)

    def _assess_risk(self, plant: Plant) -> str:
        """Assess risk level"""
        chars = (plant.characteristics or '').lower()

        if 'toxic' in chars or 'poisonous' in chars:
            return 'high'
        elif 'thorns' in chars or 'spines' in chars or 'pollen' in chars:
            return 'medium'

        return 'low'

    def _calculate_confidence(self, plant: Plant) -> float:
        """Calculate confidence score"""
        score = 100

        if not plant.plant_spacing:
            score -= 10
        if not plant.characteristics:
            score -= 15
        if not plant.position:
            score -= 10
        if not plant.days_to_maturity:
            score -= 20

        return max(50, score)

    def _calculate_suitability_score(
        self,
        metrics: ImpactMetrics,
        preferences: UserPreferences
    ) -> SuitabilityScore:
        """Calculate preference-aware suitability score"""

        weights = self._get_suitability_weights(preferences.goal)

        # Normalize metrics to 0-1 scale
        normalized = {
            'cooling': metrics.cooling_index / 100,
            'air_quality': metrics.air_quality_improvement / 100,
            'biodiversity': metrics.biodiversity_score / 100,
            'co2': min(1.0, metrics.co2_uptake_kg_year / 5.0),  # Scale to reasonable max
            'maintenance': max(0, 1.0 - metrics.maintenance_mins_week / 30),  # Invert (lower is better)
            'water_need': max(0, 1.0 - metrics.water_need_l_week / 10),  # Invert (lower is better)
            'risk': 1.0 if metrics.risk_level == 'low' else (0.5 if metrics.risk_level == 'medium' else 0.0),
            'confidence': metrics.confidence_score / 100
        }

        # Add edible yield for relevant goals
        if metrics.edible_yield_g_week and preferences.goal in ['edible', 'mixed']:
            normalized['yield'] = min(1.0, metrics.edible_yield_g_week / 100)
        else:
            normalized['yield'] = 0.0

        # Calculate weighted score
        total_score = sum(weights[key] * normalized[key] for key in weights.keys() if key in normalized)

        # Scale to 0-100
        final_score = total_score * 100

        breakdown = {key: weights[key] * normalized.get(key, 0) * 100 for key in weights.keys()}

        return SuitabilityScore(
            total_score=final_score,
            breakdown=breakdown
        )

    def _get_suitability_weights(self, goal: str) -> Dict[str, float]:
        """Get weighting factors for suitability scoring based on user goal"""

        weight_configs = {
            'edible': {
                'yield': 0.4,
                'cooling': 0.2,
                'air_quality': 0.1,
                'biodiversity': 0.1,
                'maintenance': -0.1,
                'water_need': -0.1,
                'risk': 0.1,
                'confidence': 0.1
            },
            'ornamental': {
                'cooling': 0.25,
                'air_quality': 0.2,
                'biodiversity': 0.25,
                'co2': 0.15,
                'maintenance': -0.05,
                'water_need': -0.05,
                'risk': 0.1,
                'confidence': 0.1
            },
            'mixed': {
                'yield': 0.25,
                'cooling': 0.25,
                'air_quality': 0.15,
                'biodiversity': 0.15,
                'co2': 0.1,
                'maintenance': -0.1,
                'water_need': -0.1,
                'risk': 0.1,
                'confidence': 0.1
            }
        }

        return weight_configs.get(goal, weight_configs['mixed'])

    def _convert_to_user_impact(
        self,
        metrics: ImpactMetrics,
        plant_count: int = 1
    ) -> QuantifiedImpact:
        """Convert metrics to user-facing impact display"""

        # Scale metrics by plant count
        scaled_co2 = metrics.co2_uptake_kg_year * plant_count
        scaled_water = metrics.water_cycling_l_week * plant_count
        scaled_yield = metrics.edible_yield_g_week * plant_count if metrics.edible_yield_g_week else None
        scaled_water_need = metrics.water_need_l_week * plant_count

        return QuantifiedImpact(
            temperature_reduction_c=round(self._map_cooling_to_temperature(metrics.cooling_index), 1),
            air_quality_points=self._map_aqi_to_points(metrics.air_quality_improvement),
            co2_absorption_kg_year=round(scaled_co2, 1),
            water_processed_l_week=round(scaled_water, 1),
            pollinator_support=self._map_biodiversity_to_support(metrics.biodiversity_score),
            edible_yield=f"{round(scaled_yield)}g/week after day 45" if scaled_yield else None,
            maintenance_time=f"{int(metrics.maintenance_mins_week)}mins/week",
            water_requirement=f"{round(scaled_water_need, 1)}L/week",
            risk_badge=metrics.risk_level,
            confidence_level=self._map_confidence_to_level(metrics.confidence_score),
            why_this_plant=self._generate_why_explanation(metrics)
        )

    def _map_cooling_to_temperature(self, cooling_index: float) -> float:
        """Map cooling index to temperature reduction"""
        return max(0.1, min(2.0, 0.15 * cooling_index / 10))

    def _map_aqi_to_points(self, aqi_improvement: float) -> int:
        """Map AQI improvement to points"""
        return round(max(0, min(15, aqi_improvement * 15 / 100)))

    def _map_biodiversity_to_support(self, biodiversity_score: float) -> str:
        """Map biodiversity score to support level"""
        if biodiversity_score >= 80:
            return 'High'
        elif biodiversity_score >= 60:
            return 'Medium'
        elif biodiversity_score >= 40:
            return 'Low'
        return 'Minimal'

    def _map_confidence_to_level(self, confidence_score: float) -> str:
        """Map confidence score to level"""
        if confidence_score >= 85:
            return f"High ({int(confidence_score)}%)"
        elif confidence_score >= 70:
            return f"Medium ({int(confidence_score)}%)"
        return f"Low ({int(confidence_score)}%)"

    def _generate_why_explanation(self, metrics: ImpactMetrics) -> str:
        """Generate why this plant explanation"""
        reasons = []

        if metrics.cooling_index > 70:
            reasons.append('excellent cooling effect')
        if metrics.air_quality_improvement > 60:
            reasons.append('strong air purification')
        if metrics.biodiversity_score > 70:
            reasons.append('great pollinator support')
        if metrics.edible_yield_g_week and metrics.edible_yield_g_week > 50:
            reasons.append('good edible yield')
        if metrics.maintenance_mins_week < 10:
            reasons.append('low maintenance')
        if metrics.risk_level == 'low':
            reasons.append('safe for families')

        return f"Selected for: {', '.join(reasons)}" if reasons else 'Well-suited for your conditions'

    def _calculate_community_impact(
        self,
        impact: QuantifiedImpact,
        suburb: Suburb,
        plant_count: int
    ) -> Optional[str]:
        """Calculate potential community impact"""
        if not suburb:
            return None

        # Simple community impact calculation
        # If 1 in 20 households adds this plant, estimate collective impact
        household_adoption_rate = 0.05  # 5% adoption
        estimated_households = 1000  # Rough estimate for suburb households

        collective_cooling = impact.temperature_reduction_c * household_adoption_rate * estimated_households

        if collective_cooling > 0.1:
            return f"If adopted by 5% of {suburb.name} households, could contribute ~{round(collective_cooling, 1)}°C cooling effect community-wide"

        return None