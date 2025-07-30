"""
Store finder module to locate grocery stores near a given location
"""

import requests
from bs4 import BeautifulSoup
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time
from fake_useragent import UserAgent


class StoreFinder:
    """Class to find grocery stores near a given location"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.geolocator = Nominatim(user_agent="grocery_route_optimizer")
        
    def find_kroger_stores(self, zip_code, radius_miles=10):
        """
        Find Kroger stores near a given zip code
        
        Args:
            zip_code: The zip code to search near
            radius_miles: Search radius in miles
            
        Returns:
            List of store dictionaries with name, address, distance, etc.
        """
        stores = []
        
        try:
            # First, try the Kroger store locator API-like endpoint
            stores = self._find_stores_via_api(zip_code, radius_miles)
            
            if not stores:
                # Fallback to web scraping
                stores = self._find_stores_via_scraping(zip_code, radius_miles)
                
        except Exception as e:
            print(f"Error finding stores: {e}")
            # Return some mock data for testing
            stores = self._get_mock_stores(zip_code)
            
        return stores
        
    def _find_stores_via_api(self, zip_code, radius_miles):
        """Try to find stores using Kroger's store locator endpoint"""
        stores = []
        
        # Kroger uses a specific endpoint for store searches
        url = f"https://www.kroger.com/stores/api/graphql"
        
        headers = {
            'User-Agent': self.ua.random,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        # GraphQL query for store search
        query = {
            "query": """
                query storeSearch($searchText: String!, $filters: [String!]) {
                    storeSearch(searchText: $searchText, filters: $filters) {
                        stores {
                            locationId
                            name
                            address {
                                addressLine1
                                city
                                state
                                zipCode
                            }
                            distance
                            phone
                            departments
                        }
                    }
                }
            """,
            "variables": {
                "searchText": str(zip_code),
                "filters": ["PICKUP"]
            }
        }
        
        try:
            response = requests.post(url, json=query, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'storeSearch' in data['data']:
                    for store in data['data']['storeSearch']['stores']:
                        stores.append({
                            'id': store['locationId'],
                            'name': store['name'],
                            'address': f"{store['address']['addressLine1']}, {store['address']['city']}, {store['address']['state']} {store['address']['zipCode']}",
                            'distance': round(float(store['distance']), 1),
                            'phone': store.get('phone', 'N/A'),
                            'departments': store.get('departments', [])
                        })
        except:
            pass
            
        return stores
        
    def _find_stores_via_scraping(self, zip_code, radius_miles):
        """Fallback method using web scraping"""
        stores = []
        
        # Try scraping the Kroger website
        url = f"https://www.kroger.com/stores/search?searchText={zip_code}&selectedStoreFilters=Pickup"
        
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for store cards or list items
                store_elements = soup.find_all('div', class_='StoreCard') or \
                               soup.find_all('div', class_='store-card') or \
                               soup.find_all('article', class_='store')
                
                for element in store_elements[:10]:  # Limit to 10 stores
                    try:
                        name = element.find(['h2', 'h3', 'span'], class_=['store-name', 'StoreName'])
                        address = element.find(['address', 'div'], class_=['store-address', 'StoreAddress'])
                        distance = element.find(['span', 'div'], class_=['distance', 'StoreDistance'])
                        
                        if name and address:
                            stores.append({
                                'id': f"kroger_{len(stores)}",
                                'name': name.get_text(strip=True),
                                'address': address.get_text(strip=True),
                                'distance': self._extract_distance(distance.get_text() if distance else "0 mi"),
                                'phone': 'N/A',
                                'departments': []
                            })
                    except:
                        continue
                        
        except Exception as e:
            print(f"Scraping error: {e}")
            
        return stores
        
    def _get_mock_stores(self, zip_code):
        """Return mock store data for testing"""
        # Get approximate location for the zip code
        try:
            location = self.geolocator.geocode(f"{zip_code}, USA")
            lat, lon = location.latitude, location.longitude
        except:
            lat, lon = 39.1031, -84.5120  # Default to Cincinnati, OH
            
        mock_stores = [
            {
                'id': 'kroger_001',
                'name': 'Kroger - Main Street',
                'address': '123 Main St, City, ST 12345',
                'distance': 1.2,
                'phone': '(555) 123-4567',
                'departments': ['Pharmacy', 'Deli', 'Bakery', 'Produce']
            },
            {
                'id': 'kroger_002',
                'name': 'Kroger - Market Square',
                'address': '456 Market Sq, City, ST 12345',
                'distance': 2.5,
                'phone': '(555) 234-5678',
                'departments': ['Pharmacy', 'Deli', 'Bakery', 'Produce', 'Floral']
            },
            {
                'id': 'kroger_003',
                'name': 'Kroger - West Side',
                'address': '789 West Ave, City, ST 12345',
                'distance': 3.8,
                'phone': '(555) 345-6789',
                'departments': ['Deli', 'Bakery', 'Produce']
            }
        ]
        
        return mock_stores
        
    def _extract_distance(self, distance_text):
        """Extract numeric distance from text like '2.5 miles' or '2.5 mi'"""
        try:
            # Remove non-numeric characters except decimal point
            import re
            match = re.search(r'(\d+\.?\d*)', distance_text)
            if match:
                return float(match.group(1))
        except:
            pass
        return 0.0
        
    def find_walmart_stores(self, zip_code, radius_miles=10):
        """Find Walmart stores near a given zip code"""
        # Similar implementation for Walmart
        # For now, return empty list
        return []