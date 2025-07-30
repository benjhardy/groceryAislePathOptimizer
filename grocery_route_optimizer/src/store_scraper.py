"""
Store scraper module to find item locations within grocery stores
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent


class KrogerScraper:
    """Scraper to find item locations in Kroger stores"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.use_selenium = False  # Start without selenium, enable if needed
        
    def find_item_locations(self, items, store_id):
        """
        Find the locations of items in a specific Kroger store
        
        Args:
            items: List of item names to search for
            store_id: The Kroger store ID
            
        Returns:
            Dictionary mapping item names to their locations
        """
        locations = {}
        
        # Try API-based approach first
        for item in items:
            location = self._find_item_via_api(item, store_id)
            if not location and self.use_selenium:
                location = self._find_item_via_selenium(item, store_id)
            if not location:
                location = self._get_mock_location(item)
            locations[item] = location
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        return locations
        
    def _find_item_via_api(self, item_name, store_id):
        """Try to find item location using Kroger's product search API"""
        try:
            # Kroger product search endpoint
            url = "https://www.kroger.com/products/api/products/search"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            
            params = {
                'filter.term': item_name,
                'filter.locationId': store_id,
                'filter.limit': 10,
            }
            
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for the first matching product
                if 'data' in data and 'products' in data['data']:
                    for product in data['data']['products']:
                        # Extract aisle information if available
                        if 'aisleLocations' in product:
                            locations = product['aisleLocations']
                            if locations and len(locations) > 0:
                                aisle = locations[0].get('description', '')
                                if aisle:
                                    return f"Aisle {aisle}"
                                    
                        # Check for department information
                        if 'department' in product:
                            return product['department']
                            
        except Exception as e:
            print(f"API error for {item_name}: {e}")
            
        return None
        
    def _find_item_via_selenium(self, item_name, store_id):
        """Use Selenium to find item location by searching on Kroger website"""
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={self.ua.random}')
            
            # Initialize driver
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            
            # Navigate to Kroger search
            search_url = f"https://www.kroger.com/search?query={item_name}&searchType=default_search"
            driver.get(search_url)
            
            # Wait for results to load
            wait = WebDriverWait(driver, 10)
            
            # Look for product cards
            products = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="product-card"]'))
            )
            
            for product in products[:3]:  # Check first 3 results
                try:
                    # Look for aisle information
                    aisle_elem = product.find_element(By.CSS_SELECTOR, '[data-testid="aisle-info"]')
                    if aisle_elem:
                        location = aisle_elem.text
                        driver.quit()
                        return location
                except:
                    continue
                    
            driver.quit()
            
        except Exception as e:
            print(f"Selenium error for {item_name}: {e}")
            
        return None
        
    def _get_mock_location(self, item_name):
        """Return mock location data based on common grocery store layouts"""
        # Common item categories and their typical locations
        item_locations = {
            # Produce
            'banana': 'Produce Section',
            'apple': 'Produce Section',
            'orange': 'Produce Section',
            'tomato': 'Produce Section',
            'lettuce': 'Produce Section',
            'carrot': 'Produce Section',
            'potato': 'Produce Section',
            'onion': 'Produce Section',
            'asparagus': 'Produce Section',
            
            # Dairy
            'milk': 'Aisle 1 - Dairy',
            'cheese': 'Aisle 1 - Dairy',
            'yogurt': 'Aisle 1 - Dairy',
            'butter': 'Aisle 1 - Dairy',
            'cream': 'Aisle 1 - Dairy',
            
            # Meat
            'chicken': 'Meat Department',
            'beef': 'Meat Department',
            'pork': 'Meat Department',
            'turkey': 'Meat Department',
            'fish': 'Seafood Department',
            'salmon': 'Seafood Department',
            
            # Bakery
            'bread': 'Bakery Section',
            'bagel': 'Bakery Section',
            'muffin': 'Bakery Section',
            'cake': 'Bakery Section',
            
            # Pantry
            'rice': 'Aisle 5 - Grains & Pasta',
            'pasta': 'Aisle 5 - Grains & Pasta',
            'cereal': 'Aisle 4 - Breakfast',
            'oatmeal': 'Aisle 4 - Breakfast',
            'peanut butter': 'Aisle 12 - Condiments',
            'jelly': 'Aisle 12 - Condiments',
            'jam': 'Aisle 12 - Condiments',
            'oil': 'Aisle 11 - Cooking Oils',
            'vinegar': 'Aisle 11 - Cooking Oils',
            
            # Canned Goods
            'soup': 'Aisle 7 - Canned Goods',
            'beans': 'Aisle 7 - Canned Goods',
            'corn': 'Aisle 7 - Canned Goods',
            'tuna': 'Aisle 7 - Canned Goods',
            
            # Snacks
            'chips': 'Aisle 8 - Snacks',
            'crackers': 'Aisle 8 - Snacks',
            'cookies': 'Aisle 8 - Snacks',
            'nuts': 'Aisle 8 - Snacks',
            
            # Beverages
            'water': 'Aisle 10 - Beverages',
            'soda': 'Aisle 10 - Beverages',
            'juice': 'Aisle 10 - Beverages',
            'coffee': 'Aisle 9 - Coffee & Tea',
            'tea': 'Aisle 9 - Coffee & Tea',
            
            # Frozen
            'ice cream': 'Frozen Foods',
            'frozen vegetables': 'Frozen Foods',
            'frozen pizza': 'Frozen Foods',
            
            # Other
            'eggs': 'Aisle 1 - Dairy',
            'sugar': 'Aisle 6 - Baking',
            'flour': 'Aisle 6 - Baking',
            'salt': 'Aisle 11 - Spices',
            'pepper': 'Aisle 11 - Spices',
        }
        
        # Try to match item name with known categories
        item_lower = item_name.lower()
        
        # Direct match
        if item_lower in item_locations:
            return item_locations[item_lower]
            
        # Partial match
        for key, location in item_locations.items():
            if key in item_lower or item_lower in key:
                return location
                
        # Category-based matching
        if any(word in item_lower for word in ['fruit', 'vegetable', 'veggie', 'salad']):
            return 'Produce Section'
        elif any(word in item_lower for word in ['meat', 'chicken', 'beef', 'pork']):
            return 'Meat Department'
        elif any(word in item_lower for word in ['milk', 'cheese', 'yogurt', 'dairy']):
            return 'Aisle 1 - Dairy'
        elif any(word in item_lower for word in ['bread', 'cake', 'pastry', 'donut']):
            return 'Bakery Section'
        elif any(word in item_lower for word in ['frozen', 'ice']):
            return 'Frozen Foods'
        elif any(word in item_lower for word in ['can', 'canned']):
            return 'Aisle 7 - Canned Goods'
        elif any(word in item_lower for word in ['snack', 'chip', 'cookie']):
            return 'Aisle 8 - Snacks'
        elif any(word in item_lower for word in ['drink', 'beverage', 'soda', 'juice']):
            return 'Aisle 10 - Beverages'
            
        # Default to general grocery aisle
        return 'Aisle 3 - General Grocery'
        
    def get_store_map(self, store_id):
        """
        Try to get the store map/layout
        
        Args:
            store_id: The Kroger store ID
            
        Returns:
            URL or path to store map image, or None if not found
        """
        # Most grocery stores don't publicly share detailed maps
        # This would require either:
        # 1. User uploading their own map
        # 2. Scraping from mobile app (complex)
        # 3. Using in-store kiosk data (not publicly available)
        
        return None