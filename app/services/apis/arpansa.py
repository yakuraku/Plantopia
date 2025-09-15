"""
ARPANSA UV Index API Client
Australian Radiation Protection and Nuclear Safety Agency
Provides UV index data for Australian cities
"""
import aiohttp
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class ARPANSAClient:
    """Client for fetching UV index data from ARPANSA"""
    
    BASE_URL = "https://uvdata.arpansa.gov.au/xml/uvvalues.xml"
    
    async def get_uv_index(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current UV index for Melbourne.
        
        Returns:
            UV data dictionary or None if error
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.BASE_URL, timeout=10) as response:
                    if response.status == 200:
                        content = await response.read()
                        # Handle BOM (Byte Order Mark) if present
                        if content.startswith(b'\xef\xbb\xbf'):
                            content = content[3:]
                        xml_text = content.decode('utf-8')
                        return self._parse_uv_xml(xml_text)
                    else:
                        logger.warning(f"ARPANSA API returned status {response.status}")
                        return None
                        
        except aiohttp.ClientTimeout:
            logger.error("ARPANSA API request timed out")
            return None
        except Exception as e:
            logger.error(f"Error fetching UV data: {e}")
            return None
    
    def _parse_uv_xml(self, xml_content: str) -> Optional[Dict[str, Any]]:
        """
        Parse ARPANSA XML response to extract Melbourne UV data.
        
        Args:
            xml_content: XML string from ARPANSA
            
        Returns:
            Parsed UV data for Melbourne
        """
        try:
            # Remove BOM if present in string
            if xml_content.startswith('\ufeff'):
                xml_content = xml_content[1:]
            
            root = ET.fromstring(xml_content)
            
            # Find Melbourne data (typically identified as 'mel' in ARPANSA data)
            for location in root.findall('.//location'):
                location_id = location.get('id', '')
                name_elem = location.find('name')
                name_code = name_elem.text if name_elem is not None else ''
                
                # Look for Melbourne
                if name_code.lower() == 'mel' or 'melbourne' in location_id.lower():
                    # Extract UV index value
                    index_elem = location.find('index')
                    uv_index = None
                    if index_elem is not None:
                        try:
                            uv_index = float(index_elem.text)
                        except (ValueError, TypeError):
                            uv_index = None
                    
                    # Extract time and date
                    time_elem = location.find('time')
                    time_str = time_elem.text if time_elem is not None else ''
                    
                    date_elem = location.find('date')
                    date_str = date_elem.text if date_elem is not None else ''
                    
                    # Extract status
                    status_elem = location.find('status')
                    status = status_elem.text if status_elem is not None else 'NA'
                    
                    if status == 'OK' and uv_index is not None:
                        return {
                            "uv_index": uv_index,
                            "uv_category": self._get_uv_category(uv_index),
                            "uv_protection_required": "Yes" if uv_index >= 3 else "No",
                            "measurement_time": f"{date_str} {time_str}",
                            "status": status,
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "arpansa"
                        }
            
            logger.warning("Melbourne UV data not found in ARPANSA response")
            return None
            
        except ET.ParseError as e:
            logger.error(f"Error parsing UV XML: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing UV data: {e}")
            return None
    
    def _get_uv_category(self, uv_index: float) -> str:
        """
        Get UV category based on index value.
        
        Args:
            uv_index: UV index value
            
        Returns:
            UV category string
        """
        if uv_index < 3:
            return "Low"
        elif uv_index < 6:
            return "Moderate"
        elif uv_index < 8:
            return "High"
        elif uv_index < 11:
            return "Very High"
        else:
            return "Extreme"
    
    async def get_melbourne_uv(self) -> Optional[Dict[str, Any]]:
        """
        Convenience method to get Melbourne UV data.
        
        Returns:
            UV data for Melbourne
        """
        return await self.get_uv_index()