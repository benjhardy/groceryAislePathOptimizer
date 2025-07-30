#!/usr/bin/env python3
"""
Test script for the Grocery Route Optimizer
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from src.store_finder import StoreFinder
from src.store_scraper import KrogerScraper
from src.route_optimizer import RouteOptimizer


def test_store_finder():
    """Test the store finder functionality"""
    print("Testing Store Finder...")
    finder = StoreFinder()
    stores = finder.find_kroger_stores("45202")  # Cincinnati zip code
    
    print(f"Found {len(stores)} stores:")
    for store in stores[:3]:
        print(f"  - {store['name']} at {store['address']} ({store['distance']} miles)")
    print()


def test_item_locator():
    """Test the item location finder"""
    print("Testing Item Locator...")
    scraper = KrogerScraper()
    
    test_items = ["Milk", "Bread", "Bananas", "Peanut Butter", "Chicken"]
    locations = scraper.find_item_locations(test_items, "kroger_001")
    
    print("Item locations:")
    for item, location in locations.items():
        print(f"  - {item}: {location}")
    print()


def test_route_optimizer():
    """Test the route optimization"""
    print("Testing Route Optimizer...")
    optimizer = RouteOptimizer()
    
    # Test items with locations
    items_with_locations = [
        ("Milk", "Aisle 1 - Dairy"),
        ("Bread", "Bakery Section"),
        ("Bananas", "Produce Section"),
        ("Peanut Butter", "Aisle 12 - Condiments"),
        ("Chicken", "Meat Department"),
        ("Yogurt", "Aisle 1 - Dairy"),
        ("Tomatoes", "Produce Section"),
    ]
    
    optimized = optimizer.optimize_route(items_with_locations)
    
    print("Optimized shopping route:")
    for i, (item, location) in enumerate(optimized, 1):
        print(f"  {i}. {item} - {location}")
        
    # Calculate total distance
    distance = optimizer.get_route_distance(optimized)
    print(f"\nTotal route distance: {distance} units")
    print()


def main():
    """Run all tests"""
    print("=" * 50)
    print("Grocery Route Optimizer - Component Tests")
    print("=" * 50)
    print()
    
    test_store_finder()
    test_item_locator()
    test_route_optimizer()
    
    print("All tests completed!")
    print("\nTo run the full application, use: python main.py")


if __name__ == "__main__":
    main()