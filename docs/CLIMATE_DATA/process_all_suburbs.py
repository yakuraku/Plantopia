#!/usr/bin/env python3
"""
Process ALL Melbourne suburbs climate data
This will take approximately 30-40 seconds for 151 suburbs
"""

import json
from datetime import datetime
from melbourne_climate_optimized import OptimizedClimateIntegration, get_all_melbourne_suburbs

def main():
    print("Melbourne Climate Data - FULL SUBURB PROCESSING")
    print("="*60)
    
    # Your WAQI token
    WAQI_TOKEN = "8f165ed38392c6e9659cc35b122eedd534fde40d"
    
    # Initialize integration
    integration = OptimizedClimateIntegration(waqi_token=WAQI_TOKEN)
    
    # Get all suburbs
    all_suburbs = get_all_melbourne_suburbs()
    print(f"Total suburbs to process: {len(all_suburbs)}")
    print(f"Estimated time: {len(all_suburbs) * 0.25:.0f} seconds")
    print("\nStarting processing...")
    print("-"*60)
    
    # Process all suburbs
    start_time = datetime.now()
    all_data = integration.process_suburbs(all_suburbs)
    end_time = datetime.now()
    
    # Calculate statistics
    temps = []
    aqis = []
    for suburb, data in all_data.items():
        if data.get("weather", {}).get("temperature"):
            temps.append(data["weather"]["temperature"])
        if data.get("air_quality", {}).get("aqi"):
            aqis.append(data["air_quality"]["aqi"])
    
    # Summary statistics
    print("\n" + "="*60)
    print("PROCESSING COMPLETE")
    print("="*60)
    print(f"Suburbs processed: {len(all_data)}")
    print(f"Processing time: {(end_time - start_time).seconds} seconds")
    
    if temps:
        print(f"\nTemperature Statistics:")
        print(f"  Minimum: {min(temps):.1f}°C")
        print(f"  Maximum: {max(temps):.1f}°C")
        print(f"  Average: {sum(temps)/len(temps):.1f}°C")
        print(f"  Range: {max(temps)-min(temps):.1f}°C")
    
    if aqis:
        print(f"\nAir Quality Statistics:")
        print(f"  Best AQI: {min(aqis)}")
        print(f"  Worst AQI: {max(aqis)}")
        print(f"  Average AQI: {sum(aqis)/len(aqis):.1f}")
    
    # Find extremes
    coldest = min(all_data.items(), key=lambda x: x[1].get("weather", {}).get("temperature", float('inf')))
    warmest = max(all_data.items(), key=lambda x: x[1].get("weather", {}).get("temperature", float('-inf')))
    
    print(f"\nExtreme Suburbs:")
    print(f"  Coldest: {coldest[0]} ({coldest[1]['weather']['temperature']:.1f}°C)")
    print(f"  Warmest: {warmest[0]} ({warmest[1]['weather']['temperature']:.1f}°C)")
    
    # Save full data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"melbourne_all_suburbs_climate_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\n✓ Complete climate data saved to: {filename}")
    print(f"  File contains data for {len(all_data)} suburbs")
    
    # Group by regions for summary
    regions = {
        "Central": ["Melbourne CBD", "Carlton", "Docklands", "Southbank"],
        "North": ["Brunswick", "Preston", "Coburg", "Craigieburn"],
        "East": ["Box Hill", "Ringwood", "Glen Waverley", "Doncaster"],
        "South": ["St Kilda", "Brighton", "Frankston", "Mentone"],
        "West": ["Footscray", "Sunshine", "Werribee", "Altona"]
    }
    
    print("\nRegional Summary:")
    for region, suburbs in regions.items():
        region_temps = []
        for suburb in suburbs:
            if suburb in all_data and all_data[suburb].get("weather", {}).get("temperature"):
                region_temps.append(all_data[suburb]["weather"]["temperature"])
        if region_temps:
            avg_temp = sum(region_temps) / len(region_temps)
            print(f"  {region}: {avg_temp:.1f}°C average")
    
    print("\n" + "="*60)
    print("Data successfully collected for all Melbourne suburbs!")
    print("Including weather, air quality, and UV index data.")


if __name__ == "__main__":
    main()