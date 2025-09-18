"""
Script to enrich plant data with recommendation engine fields
"""
import asyncio
import pandas as pd
import re
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal
from app.models.database import Plant
from app.core.config import settings


def parse_sun_requirements(position_str):
    """Extract sun requirements from position field"""
    if not position_str or pd.isna(position_str):
        return "part_sun"  # Default
    
    position_lower = str(position_str).lower()
    
    if "full sun" in position_lower:
        return "full_sun"
    elif "part sun" in position_lower or "partial" in position_lower:
        return "part_sun"
    elif "shade" in position_lower:
        return "bright_shade"
    else:
        return "part_sun"  # Default


def parse_sowing_months(period_str):
    """Convert sowing period string to list of months"""
    if not period_str or pd.isna(period_str):
        return []
    
    months = []
    period_str = str(period_str)
    
    # Split by comma or "and"
    parts = re.split(r',|\s+and\s+', period_str)
    
    for part in parts:
        part = part.strip()
        if part and not part.lower() == 'nan':
            months.append(part)
    
    return months


def parse_days_to_maturity(days_str):
    """Extract days to maturity as integer"""
    if not days_str or pd.isna(days_str):
        return None

    days_str = str(days_str).lower()

    # Check if it contains "year" and convert to days
    if 'year' in days_str:
        # Extract numbers before handling years
        numbers = re.findall(r'\d+', days_str)
        if numbers:
            # If it's something like "2 years" or "1-2 years"
            if len(numbers) == 1:
                return int(numbers[0]) * 365
            elif len(numbers) >= 2:
                # Average for ranges like "1-2 years"
                avg_years = (int(numbers[0]) + int(numbers[1])) / 2
                return int(avg_years * 365)

    # Look for number patterns (for days)
    numbers = re.findall(r'\d+', days_str)
    if numbers:
        # Return the first number found (or average if range)
        if len(numbers) == 1:
            return int(numbers[0])
        elif len(numbers) >= 2:
            return (int(numbers[0]) + int(numbers[1])) // 2

    return None


def parse_spacing(spacing_str):
    """Extract spacing in cm"""
    if not spacing_str or pd.isna(spacing_str):
        return None
    
    spacing_str = str(spacing_str)
    
    # Look for number patterns
    numbers = re.findall(r'\d+', spacing_str)
    if numbers:
        return int(numbers[0])
    
    return None


def parse_sowing_depth(depth_str):
    """Extract sowing depth in mm"""
    if not depth_str or pd.isna(depth_str):
        return None
    
    depth_str = str(depth_str)
    
    # Look for number patterns
    numbers = re.findall(r'\d+', depth_str)
    if numbers:
        # Convert to mm if needed
        depth = int(numbers[0])
        if "cm" in depth_str.lower():
            depth = depth * 10  # Convert cm to mm
        return depth
    
    return None


def check_container_suitability(row):
    """Determine if plant is suitable for containers"""
    # Check description and characteristics
    text_to_check = str(row.get('description', '')) + ' ' + str(row.get('characteristics', ''))
    text_lower = text_to_check.lower()
    
    # Keywords indicating container suitability
    container_keywords = ['container', 'pot', 'balcony', 'compact', 'dwarf', 'small space']
    
    for keyword in container_keywords:
        if keyword in text_lower:
            return True
    
    # Herbs are generally container-friendly
    if row.get('plant_category') == 'herb':
        return True
    
    return False


def check_indoor_suitability(row):
    """Determine if plant can grow indoors"""
    text_to_check = str(row.get('description', '')) + ' ' + str(row.get('characteristics', ''))
    text_lower = text_to_check.lower()
    
    # Keywords indicating indoor suitability
    indoor_keywords = ['indoor', 'houseplant', 'inside']
    
    for keyword in indoor_keywords:
        if keyword in text_lower:
            return True
    
    # Some herbs can grow indoors
    if row.get('plant_category') == 'herb' and row.get('position'):
        if 'shade' in str(row['position']).lower():
            return True
    
    return False


def check_fragrant(row):
    """Check if plant is fragrant"""
    text_to_check = str(row.get('description', '')) + ' ' + str(row.get('characteristics', ''))
    text_lower = text_to_check.lower()
    
    fragrant_keywords = ['fragrant', 'scented', 'aromatic', 'perfume', 'smell']
    
    for keyword in fragrant_keywords:
        if keyword in text_lower:
            return True
    
    # Most herbs are fragrant
    if row.get('plant_category') == 'herb':
        return True
    
    return False


def extract_flower_colors(row):
    """Extract flower colors from description"""
    if row.get('plant_category') != 'flower':
        return []
    
    text_to_check = str(row.get('description', '')) + ' ' + str(row.get('characteristics', ''))
    text_lower = text_to_check.lower()
    
    colors = []
    color_keywords = ['white', 'yellow', 'orange', 'red', 'pink', 'purple', 'blue', 'lavender', 'violet']
    
    for color in color_keywords:
        if color in text_lower:
            colors.append(color)
    
    return colors


def calculate_maintainability_score(row):
    """Calculate maintainability score (0.0 to 1.0)"""
    text_to_check = str(row.get('description', '')) + ' ' + str(row.get('characteristics', ''))
    text_lower = text_to_check.lower()
    
    # High maintainability (easy care)
    if any(word in text_lower for word in ['easy', 'low maintenance', 'hardy', 'drought tolerant', 'tough']):
        return 0.8
    
    # Low maintainability (high care)
    if any(word in text_lower for word in ['difficult', 'high maintenance', 'delicate', 'sensitive']):
        return 0.3
    
    # Default medium
    return 0.5


async def enrich_plants():
    """Enrich plant data with recommendation engine fields"""
    print("🌱 Enriching plant data...")
    
    async with AsyncSessionLocal() as session:
        # Get all plants
        result = await session.execute(select(Plant))
        plants = result.scalars().all()
        
        print(f"Found {len(plants)} plants to enrich")
        
        # Process each CSV file for additional data
        for category, csv_path in settings.CSV_PATHS.items():
            if not Path(csv_path).exists():
                print(f"⚠️  {csv_path} not found, skipping")
                continue
            
            print(f"\n📊 Processing {category} plants from CSV...")
            df = pd.read_csv(csv_path)
            
            # Process each plant
            plants_updated = 0
            for _, row in df.iterrows():
                plant_name = row.get('plant_name', row.get('name'))
                if not plant_name:
                    continue
                
                # Find matching plant in database
                matching_plant = None
                for plant in plants:
                    if plant.plant_name and plant_name.lower() in plant.plant_name.lower():
                        matching_plant = plant
                        break
                
                if not matching_plant:
                    continue
                
                # Update plant with enriched data
                matching_plant.sun_need = parse_sun_requirements(row.get('position'))
                matching_plant.edible = category in ['herb', 'vegetable']
                matching_plant.container_ok = check_container_suitability(row)
                matching_plant.indoor_ok = check_indoor_suitability(row)
                matching_plant.fragrant = check_fragrant(row)
                matching_plant.time_to_maturity_days = parse_days_to_maturity(row.get('days_to_maturity'))
                matching_plant.maintainability_score = calculate_maintainability_score(row)
                matching_plant.sowing_depth_mm = parse_sowing_depth(row.get('sowing_depth'))
                matching_plant.spacing_cm = parse_spacing(row.get('plant_spacing'))
                matching_plant.habit = str(row.get('hardiness_life_cycle', ''))[:100] if not pd.isna(row.get('hardiness_life_cycle')) else None
                matching_plant.sowing_method = str(row.get('sowing_method'))[:500] if not pd.isna(row.get('sowing_method')) else None
                
                # Extract flower colors for flowers
                if category == 'flower':
                    matching_plant.flower_colors = extract_flower_colors(row)
                
                # Build sowing months by climate
                sowing_by_climate = {}
                
                # Process climate-specific sowing periods
                climate_mappings = {
                    'cool': 'cool_climate_sowing_period',
                    'temperate': 'temperate_climate_sowing_period',
                    'subtropical': 'subtropical_climate_sowing_period',
                    'tropical': 'tropical_climate_sowing_period',
                    'arid': 'arid_climate_sowing_period'
                }
                
                for climate_key, csv_column in climate_mappings.items():
                    if csv_column in row:
                        months = parse_sowing_months(row[csv_column])
                        if months:
                            sowing_by_climate[climate_key] = months
                
                # Default to temperate if no specific data
                if not sowing_by_climate and row.get('season'):
                    season = str(row['season']).lower()
                    if 'spring' in season:
                        sowing_by_climate['temperate'] = ['September', 'October', 'November']
                    elif 'summer' in season:
                        sowing_by_climate['temperate'] = ['December', 'January', 'February']
                    elif 'autumn' in season or 'fall' in season:
                        sowing_by_climate['temperate'] = ['March', 'April', 'May']
                    elif 'winter' in season:
                        sowing_by_climate['temperate'] = ['June', 'July', 'August']
                
                if sowing_by_climate:
                    matching_plant.sowing_months_by_climate = sowing_by_climate
                
                plants_updated += 1
                
                if plants_updated % 50 == 0:
                    print(f"  ✓ Updated {plants_updated} {category} plants...")
            
            print(f"  ✅ Total {category} plants updated: {plants_updated}")
        
        # Commit all changes
        await session.commit()
        print("\n✅ Plant data enrichment complete!")
        
        # Show sample of enriched data
        print("\n📊 Sample enriched plant:")
        sample_plant = plants[0]
        print(f"  Name: {sample_plant.plant_name}")
        print(f"  Sun need: {sample_plant.sun_need}")
        print(f"  Edible: {sample_plant.edible}")
        print(f"  Container OK: {sample_plant.container_ok}")
        print(f"  Indoor OK: {sample_plant.indoor_ok}")
        print(f"  Maintainability: {sample_plant.maintainability_score}")
        print(f"  Sowing months: {sample_plant.sowing_months_by_climate}")


if __name__ == "__main__":
    asyncio.run(enrich_plants())