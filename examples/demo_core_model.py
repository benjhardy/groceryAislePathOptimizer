#!/usr/bin/env python3
"""
Demonstration of the core data model for the grocery route optimizer.

This script shows how to use the AisleNode, Store, Item, and RouteOptimizer
classes to model a store and optimize shopping routes.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grocery_optimizer import (
    AisleNode, Store, Item, ShoppingList, SubSection,
    get_optimizer, Route
)


def create_sample_store() -> Store:
    """Create a sample store with aisle nodes."""
    store = Store(
        name="Sample Grocery Store",
        address="123 Main Street, Sample City"
    )
    
    # Create entrance and checkout area
    entrance = AisleNode(name="Entrance", x=0, y=0)
    checkout = AisleNode(name="Checkout", x=0, y=100)
    
    # Create aisle nodes (simple grid layout)
    aisle_nodes = [
        # Produce section
        AisleNode(name="Produce", x=20, y=20, aisle_number=1),
        
        # Dairy section
        AisleNode(name="Dairy", x=40, y=20, aisle_number=2),
        
        # Meat section
        AisleNode(name="Meat", x=60, y=20, aisle_number=3),
        
        # Frozen foods
        AisleNode(name="Frozen", x=80, y=20, aisle_number=4),
        
        # Dry goods aisles
        AisleNode(name="Cereal & Breakfast", x=20, y=40, aisle_number=5),
        AisleNode(name="Canned Goods", x=40, y=40, aisle_number=6),
        AisleNode(name="Pasta & Rice", x=60, y=40, aisle_number=7),
        AisleNode(name="Snacks", x=80, y=40, aisle_number=8),
        
        # Beverages and household
        AisleNode(name="Beverages", x=20, y=60, aisle_number=9),
        AisleNode(name="Cleaning Supplies", x=40, y=60, aisle_number=10),
        AisleNode(name="Personal Care", x=60, y=60, aisle_number=11),
        AisleNode(name="Pharmacy", x=80, y=60, aisle_number=12),
    ]
    
    # Add all nodes to store
    store.add_node(entrance)
    store.add_node(checkout)
    for node in aisle_nodes:
        store.add_node(node)
    
    # Set entrance and exit
    store.entrance_node_id = entrance.id
    store.exit_node_id = checkout.id
    
    return store


def create_sample_shopping_list(store: Store) -> ShoppingList:
    """Create a sample shopping list with items from different aisles."""
    shopping_list = ShoppingList(name="Weekly Groceries")
    
    # Find nodes for items
    produce_node = next(n for n in store.nodes if n.name == "Produce")
    dairy_node = next(n for n in store.nodes if n.name == "Dairy")
    meat_node = next(n for n in store.nodes if n.name == "Meat")
    cereal_node = next(n for n in store.nodes if n.name == "Cereal & Breakfast")
    beverages_node = next(n for n in store.nodes if n.name == "Beverages")
    
    # Create items
    items = [
        Item(name="Bananas", aisle_node_id=produce_node.id, 
             sub_section=SubSection.LEFT, category="Fruit", price=1.99),
        Item(name="Milk", aisle_node_id=dairy_node.id, 
             category="Dairy", price=3.49),
        Item(name="Ground Beef", aisle_node_id=meat_node.id, 
             category="Meat", price=8.99),
        Item(name="Cheerios", aisle_node_id=cereal_node.id, 
             sub_section=SubSection.TOP_SHELF, category="Breakfast", price=4.99),
        Item(name="Orange Juice", aisle_node_id=beverages_node.id, 
             category="Beverages", price=3.99),
    ]
    
    for item in items:
        shopping_list.add_item(item)
    
    return shopping_list


def demonstrate_route_optimization():
    """Demonstrate route optimization with different algorithms."""
    print("=== Grocery Route Optimizer Demo ===\n")
    
    # Create sample store and shopping list
    print("1. Creating sample store...")
    store = create_sample_store()
    print(f"   Store: {store.name}")
    print(f"   Nodes: {len(store.nodes)}")
    print(f"   Bounds: {store.bounds}")
    
    print("\n2. Creating shopping list...")
    shopping_list = create_sample_shopping_list(store)
    print(f"   Items: {len(shopping_list.items)}")
    print(f"   Total cost: ${shopping_list.total_estimated_cost():.2f}")
    
    # Show items and their locations
    print("\n   Shopping items:")
    for item in shopping_list.items:
        location = item.get_location_description(store)
        price_str = f"${item.price:.2f}" if item.price else "N/A"
        print(f"   - {item.name} ({location}) - {price_str}")
    
    # Analyze required nodes
    required_nodes = shopping_list.get_required_nodes()
    print(f"\n   Required nodes to visit: {len(required_nodes)}")
    
    # Demonstrate different optimization algorithms
    algorithms = ['greedy', 'brute_force', 'two_opt']
    
    print("\n3. Route Optimization Results:")
    print("-" * 50)
    
    for algorithm in algorithms:
        print(f"\n{algorithm.upper()} Algorithm:")
        try:
            optimizer = get_optimizer(algorithm, store)
            route = optimizer.optimize_route(shopping_list)
            
            print(f"   Total distance: {route.total_distance:.2f} units")
            print(f"   Nodes in route: {len(route.nodes)}")
            print("   Route sequence:")
            
            for i, node in enumerate(route.nodes):
                items_here = shopping_list.get_items_at_node(node.id)
                items_str = f" (collect: {', '.join(item.name for item in items_here)})" if items_here else ""
                print(f"   {i+1:2d}. {node.name}{items_str}")
                
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n4. Store Analysis:")
    print(f"   Store bounds: {store.bounds}")
    print(f"   Entrance: {store.get_entrance_node().name if store.get_entrance_node() else 'None'}")
    print(f"   Exit: {store.get_exit_node().name if store.get_exit_node() else 'None'}")
    
    # Group items by node
    print("\n5. Items grouped by location:")
    grouped = shopping_list.group_by_node()
    for node_id, items in grouped.items():
        node = store.get_node(node_id)
        node_name = node.name if node else f"Unknown ({node_id[:8]})"
        print(f"   {node_name}: {', '.join(item.name for item in items)}")


if __name__ == "__main__":
    demonstrate_route_optimization()