#!/usr/bin/env python3
"""
ARPANSA UV Index Client for Melbourne
Fetches real-time UV index data from ARPANSA (Australian Radiation Protection and Nuclear Safety Agency)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Optional
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ARPANSAUVClient:
    """Client for accessing ARPANSA UV Index data"""
    
    def __init__(self):
        """Initialize the ARPANSA UV client"""
        self.base_url = "https://uvdata.arpansa.gov.au/xml/uvvalues.xml"
        self.forecast_url = "https://uvdata.arpansa.gov.au/forecastuvindex"
        self.current_data = None
        
    def fetch_current_uv(self) -> Optional[Dict]:
        """
        Fetch current UV index data for all Australian capital cities
        
        Returns:
            Dictionary containing UV data or None if error
        """
        try:
            logger.info(f"Fetching UV data from: {self.base_url}")
            
            response = requests.get(self.base_url, timeout=10)
            
            if response.status_code == 200:
                # Handle BOM in response content
                content = response.content
                if content.startswith(b'\xef\xbb\xbf'):
                    content = content[3:]
                xml_text = content.decode('utf-8')
                return self._parse_uv_xml(xml_text)
            else:
                logger.warning(f"Failed to fetch UV data: Status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching UV data: {e}")
            return None
    
    def _parse_uv_xml(self, xml_content: str) -> Optional[Dict]:
        """
        Parse ARPANSA UV XML data
        
        Args:
            xml_content: XML string from ARPANSA
            
        Returns:
            Parsed UV data dictionary
        """
        try:
            # Remove BOM if present
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]
            
            root = ET.fromstring(xml_content)
            
            uv_data = {}
            
            # Find all location elements
            for location in root.findall('.//location'):
                location_id = location.get('id', '')
                # The name field contains the abbreviated city code
                name_elem = location.find('name')
                name_code = name_elem.text if name_elem is not None else ''
                
                # Extract UV index value
                index_elem = location.find('index')
                uv_index = None
                if index_elem is not None:
                    try:
                        uv_index = float(index_elem.text)
                    except (ValueError, TypeError):
                        uv_index = None
                
                # Extract time
                time_elem = location.find('time')
                time_str = time_elem.text if time_elem is not None else ''
                
                # Extract date
                date_elem = location.find('date')
                date_str = date_elem.text if date_elem is not None else ''
                
                # Extract status
                status_elem = location.find('status')
                status = status_elem.text if status_elem is not None else 'NA'
                
                # Store location data using the name code as key for Melbourne lookup
                uv_data[name_code] = {
                    'location_id': location_id,
                    'name': location_id,  # Use the full location name
                    'code': name_code,
                    'uv_index': uv_index,
                    'time': time_str,
                    'date': date_str,
                    'datetime': f"{date_str} {time_str}",
                    'status': status,
                    'category': self._get_uv_category(uv_index),
                    'protection_required': self._is_protection_required(uv_index)
                }
            
            self.current_data = uv_data
            return uv_data
            
        except ET.ParseError as e:
            logger.error(f"Error parsing UV XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing UV data: {e}")
            return None
    
    def _get_uv_category(self, uv_index: Optional[float]) -> str:
        """
        Get UV category based on index value
        
        Args:
            uv_index: UV index value
            
        Returns:
            UV category string
        """
        if uv_index is None:
            return "Unknown"
        elif uv_index < 3:
            return "Low"
        elif uv_index < 6:
            return "Moderate"
        elif uv_index < 8:
            return "High"
        elif uv_index < 11:
            return "Very High"
        else:
            return "Extreme"
    
    def _is_protection_required(self, uv_index: Optional[float]) -> bool:
        """
        Determine if sun protection is required
        
        Args:
            uv_index: UV index value
            
        Returns:
            True if protection required (UV >= 3)
        """
        return uv_index is not None and uv_index >= 3
    
    def get_melbourne_uv(self) -> Optional[Dict]:
        """
        Get UV data specifically for Melbourne
        
        Returns:
            Melbourne UV data or None if not available
        """
        if not self.current_data:
            self.fetch_current_uv()
        
        if self.current_data:
            # Melbourne is typically identified as 'mel' in ARPANSA data
            return self.current_data.get('mel')
        
        return None
    
    def display_uv_data(self, location_data: Dict) -> None:
        """
        Display UV data in a formatted way
        
        Args:
            location_data: UV data for a location
        """
        print(f"\n{'='*60}")
        print(f"UV Index Report - {location_data.get('name', 'Unknown')}")
        print(f"{'='*60}")
        print(f"Date/Time: {location_data.get('datetime', 'Unknown')}")
        print(f"Status: {location_data.get('status', 'Unknown')}")
        print(f"{'-'*40}")
        
        uv_index = location_data.get('uv_index')
        if uv_index is not None:
            print(f"UV Index: {uv_index}")
            print(f"Category: {location_data.get('category', 'Unknown')}")
            
            if location_data.get('protection_required'):
                print("\n⚠️  SUN PROTECTION REQUIRED")
                print("When UV Index is 3 or above:")
                print("  • Wear sun-protective clothing")
                print("  • Apply SPF 30+ sunscreen")
                print("  • Wear a broad-brimmed hat")
                print("  • Seek shade")
                print("  • Wear sunglasses")
            else:
                print("\n✓ Sun protection not required (UV < 3)")
        else:
            print("UV Index: Data not available")
    
    def display_all_locations(self) -> None:
        """Display UV data for all available locations"""
        if not self.current_data:
            self.fetch_current_uv()
        
        if self.current_data:
            print(f"\n{'='*60}")
            print("UV Index - All Australian Capital Cities")
            print(f"{'='*60}")
            
            for location_id, data in self.current_data.items():
                if data['status'] == 'OK':
                    print(f"{data['name']:20} UV Index: {data.get('uv_index', 'N/A'):5} "
                          f"Category: {data.get('category', 'Unknown')}")
                else:
                    print(f"{data['name']:20} Data unavailable")
    
    def save_uv_data(self, filename: str = None) -> str:
        """
        Save UV data to JSON file
        
        Args:
            filename: Optional filename, defaults to timestamp
            
        Returns:
            Filename where data was saved
        """
        if not self.current_data:
            self.fetch_current_uv()
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"arpansa_uv_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.current_data, f, indent=2)
        
        logger.info(f"UV data saved to {filename}")
        return filename


def main():
    """Test ARPANSA UV data fetching"""
    
    print("ARPANSA UV Index Client")
    print("Australian Radiation Protection and Nuclear Safety Agency")
    print("="*60)
    
    # Create client
    client = ARPANSAUVClient()
    
    # Fetch current UV data
    print("\nFetching current UV index data...")
    uv_data = client.fetch_current_uv()
    
    if uv_data:
        print("✓ Successfully connected to ARPANSA!")
        
        # Display Melbourne data
        melbourne_uv = client.get_melbourne_uv()
        if melbourne_uv:
            client.display_uv_data(melbourne_uv)
        else:
            print("\n✗ Melbourne UV data not available")
        
        # Display all locations
        client.display_all_locations()
        
        # Save data
        filename = client.save_uv_data()
        print(f"\nUV data saved to: {filename}")
        
        print("\n" + "="*60)
        print("Data Attribution:")
        print("UV observations courtesy of ARPANSA")
        print("For more information: https://www.arpansa.gov.au/our-services/monitoring/ultraviolet-radiation-monitoring")
        
    else:
        print("✗ Failed to fetch UV data from ARPANSA")
        print("\nThe service might be temporarily unavailable")
        print("Try visiting: https://www.arpansa.gov.au/our-services/monitoring/ultraviolet-radiation-monitoring")


if __name__ == "__main__":
    main()