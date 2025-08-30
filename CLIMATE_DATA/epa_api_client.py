#!/usr/bin/env python3
"""
EPA Victoria Air Quality API Client
Fixed version with proper error handling and multiple endpoint support
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EPAVictoriaClient:
    """Client for accessing EPA Victoria Air Quality data with proper error handling"""
    
    def __init__(self, api_key: str):
        """
        Initialize the EPA API client
        
        Args:
            api_key: Your EPA Victoria API key
        """
        self.api_key = api_key
        
        # Try multiple possible endpoints
        self.endpoints = [
            "https://gateway.api.epa.vic.gov.au/environmentMonitoring/v1",
            "https://portal.api.epa.vic.gov.au/environment-monitoring/1",
            "https://gateway.api.epa.vic.gov.au/environment-monitoring/v1"
        ]
        
        self.base_url = None
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Rate limiting: 5 requests per second
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 200ms between requests
        
    def _rate_limit(self):
        """Enforce rate limiting to avoid 503 errors"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make HTTP request with retry logic and error handling
        
        Args:
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            JSON response or None if all attempts fail
        """
        self._rate_limit()
        
        # Try each base URL if we haven't found a working one
        if not self.base_url:
            for base in self.endpoints:
                try:
                    url = f"{base}/{endpoint}"
                    logger.info(f"Trying endpoint: {url}")
                    
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        self.base_url = base
                        logger.info(f"Success! Using base URL: {base}")
                        return response.json()
                    else:
                        logger.warning(f"Status {response.status_code} from {base}: {response.text[:200]}")
                        
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request failed for {base}: {e}")
                    continue
        else:
            # Use the known working base URL
            try:
                url = f"{self.base_url}/{endpoint}"
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 503:
                    logger.warning("503 Service Unavailable - waiting before retry...")
                    time.sleep(5)
                    return None
                else:
                    logger.warning(f"Status {response.status_code}: {response.text[:200]}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
        return None
    
    def test_connection(self) -> bool:
        """
        Test API connection and find working endpoint
        
        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Testing EPA API connection...")
        
        # Try to get sites as a test
        result = self._make_request("sites")
        
        if result:
            logger.info("API connection successful!")
            return True
        else:
            logger.error("Could not connect to EPA API with any endpoint")
            return False
    
    def get_all_sites(self) -> Optional[Dict]:
        """
        Get all monitoring sites from EPA Victoria
        
        Returns:
            Dictionary containing all monitoring sites or None if error
        """
        logger.info("Fetching all monitoring sites...")
        return self._make_request("sites")
    
    def get_site_by_id(self, site_id: str) -> Optional[Dict]:
        """
        Get details for a specific monitoring site
        
        Args:
            site_id: The ID of the monitoring site
            
        Returns:
            Dictionary containing site details or None if error
        """
        logger.info(f"Fetching site details for: {site_id}")
        return self._make_request(f"sites/{site_id}")
    
    def get_measurements_by_site(self, site_id: str) -> Optional[Dict]:
        """
        Get air quality measurements for a specific site
        
        Args:
            site_id: The ID of the monitoring site
            
        Returns:
            Dictionary containing measurements or None if error
        """
        logger.info(f"Fetching measurements for site: {site_id}")
        return self._make_request(f"sites/{site_id}/measurements")
    
    def get_latest_measurements(self) -> Optional[Dict]:
        """
        Get latest air quality measurements from all sites
        
        Returns:
            Dictionary containing latest measurements or None if error
        """
        logger.info("Fetching latest measurements from all sites...")
        return self._make_request("measurements/latest")
    
    def get_air_quality_categories(self) -> Optional[Dict]:
        """
        Get air quality category definitions
        
        Returns:
            Dictionary containing category definitions or None if error
        """
        logger.info("Fetching air quality categories...")
        return self._make_request("categories")
    
    def display_sites(self, sites_data: Dict) -> None:
        """
        Display monitoring sites in a formatted way
        
        Args:
            sites_data: Dictionary containing sites data
        """
        if not sites_data:
            print("No sites data available")
            return
            
        print("\n" + "="*60)
        print("EPA Victoria Air Quality Monitoring Sites")
        print("="*60)
        
        # Handle different response structures
        if isinstance(sites_data, dict):
            if 'records' in sites_data:
                sites = sites_data['records']
            elif 'sites' in sites_data:
                sites = sites_data['sites']
            elif 'data' in sites_data:
                sites = sites_data['data']
            else:
                sites = [sites_data]
        elif isinstance(sites_data, list):
            sites = sites_data
        else:
            sites = []
            
        for site in sites:
            # Try different possible field names
            site_id = site.get('siteId') or site.get('site_id') or site.get('id') or 'N/A'
            site_name = site.get('siteName') or site.get('name') or site.get('site_name') or 'N/A'
            site_type = site.get('siteType') or site.get('type') or site.get('site_type') or 'N/A'
            
            print(f"\nSite ID: {site_id}")
            print(f"Name: {site_name}")
            print(f"Type: {site_type}")
            
            # Location information
            if 'location' in site:
                loc = site['location']
                lat = loc.get('latitude') or loc.get('lat') or 'N/A'
                lon = loc.get('longitude') or loc.get('lon') or loc.get('lng') or 'N/A'
                print(f"Location: {lat}, {lon}")
            elif 'latitude' in site and 'longitude' in site:
                print(f"Location: {site['latitude']}, {site['longitude']}")
                
            print("-"*40)


def main():
    """Main function to test EPA API connectivity"""
    
    # Your API key
    API_KEY = "8963cdcd394644a7a475a8c6c645671e"
    
    print("EPA Victoria Air Quality API Client")
    print("Testing connection and troubleshooting 503 errors...")
    print("="*60)
    
    # Create client instance
    client = EPAVictoriaClient(API_KEY)
    
    # Test connection
    if client.test_connection():
        print("\n✓ Successfully connected to EPA API!")
        print(f"Working endpoint: {client.base_url}")
        
        # Try to fetch all sites
        sites = client.get_all_sites()
        if sites:
            client.display_sites(sites)
            
            # Save successful response for analysis
            with open('epa_sites_response.json', 'w') as f:
                json.dump(sites, f, indent=2)
            print("\nResponse saved to 'epa_sites_response.json'")
            
        # Try to fetch latest measurements
        print("\nFetching latest measurements...")
        measurements = client.get_latest_measurements()
        if measurements:
            with open('epa_measurements_response.json', 'w') as f:
                json.dump(measurements, f, indent=2)
            print("Measurements saved to 'epa_measurements_response.json'")
            
    else:
        print("\n✗ Failed to connect to EPA API")
        print("\nTroubleshooting suggestions:")
        print("1. Verify your API key is correct")
        print("2. Check if you're subscribed to the correct product on portal.api.epa.vic.gov.au")
        print("3. Try visiting https://portal.api.epa.vic.gov.au to check your subscription")
        print("4. Contact EPA at contact@epa.vic.gov.au if issues persist")
        print("\nAlternative: Use the EPA AirWatch website data directly")
        print("Visit: https://www.epa.vic.gov.au/for-community/airwatch")


if __name__ == "__main__":
    main()