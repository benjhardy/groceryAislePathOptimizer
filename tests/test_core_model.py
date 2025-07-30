#!/usr/bin/env python3
"""
Unit tests for the core data model.

Tests the AisleNode, Store, Item, ShoppingList, and RouteOptimizer classes.
"""

import unittest
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grocery_optimizer import (
    AisleNode, Store, Item, ShoppingList, SubSection,
    get_optimizer, Route
)


class TestAisleNode(unittest.TestCase):
    """Test the AisleNode class."""
    
    def test_creation_with_defaults(self):
        """Test creating an AisleNode with default values."""
        node = AisleNode()
        self.assertEqual(node.name, "")
        self.assertEqual(node.x, 0.0)
        self.assertEqual(node.y, 0.0)
        self.assertIsNone(node.aisle_number)
        self.assertIsNone(node.description)
        self.assertIsInstance(node.id, str)
    
    def test_creation_with_values(self):
        """Test creating an AisleNode with specific values."""
        node = AisleNode(name="Test Aisle", x=10.5, y=20.5, aisle_number=5)
        self.assertEqual(node.name, "Test Aisle")
        self.assertEqual(node.x, 10.5)
        self.assertEqual(node.y, 20.5)
        self.assertEqual(node.aisle_number, 5)
    
    def test_negative_coordinates_raise_error(self):
        """Test that negative coordinates raise ValueError."""
        with self.assertRaises(ValueError):
            AisleNode(x=-1, y=0)
        with self.assertRaises(ValueError):
            AisleNode(x=0, y=-1)
    
    def test_coordinates_property(self):
        """Test the coordinates property returns a tuple."""
        node = AisleNode(x=10, y=20)
        self.assertEqual(node.coordinates, (10, 20))
    
    def test_distance_calculation(self):
        """Test distance calculations between nodes."""
        node1 = AisleNode(x=0, y=0)
        node2 = AisleNode(x=3, y=4)
        
        # Euclidean distance should be 5 (3-4-5 triangle)
        self.assertEqual(node1.distance_to(node2), 5.0)
        self.assertEqual(node2.distance_to(node1), 5.0)
        
        # Manhattan distance should be 7
        self.assertEqual(node1.manhattan_distance_to(node2), 7.0)
        self.assertEqual(node2.manhattan_distance_to(node1), 7.0)


class TestStore(unittest.TestCase):
    """Test the Store class."""
    
    def setUp(self):
        """Set up test store with sample nodes."""
        self.store = Store(name="Test Store", address="123 Test St")
        self.node1 = AisleNode(name="Node 1", x=0, y=0)
        self.node2 = AisleNode(name="Node 2", x=10, y=10)
        self.node3 = AisleNode(name="Node 3", x=20, y=20)
    
    def test_empty_store_creation(self):
        """Test creating an empty store."""
        store = Store()
        self.assertEqual(store.name, "")
        self.assertEqual(store.address, "")
        self.assertEqual(len(store.nodes), 0)
        self.assertIsNone(store.entrance_node_id)
        self.assertIsNone(store.exit_node_id)
    
    def test_add_nodes(self):
        """Test adding nodes to a store."""
        self.store.add_node(self.node1)
        self.store.add_node(self.node2)
        
        self.assertEqual(len(self.store.nodes), 2)
        self.assertEqual(self.store.get_node(self.node1.id), self.node1)
        self.assertEqual(self.store.get_node(self.node2.id), self.node2)
    
    def test_add_duplicate_node_raises_error(self):
        """Test that adding a node with duplicate ID raises error."""
        self.store.add_node(self.node1)
        with self.assertRaises(ValueError):
            self.store.add_node(self.node1)
    
    def test_remove_node(self):
        """Test removing nodes from a store."""
        self.store.add_node(self.node1)
        self.store.add_node(self.node2)
        
        self.store.remove_node(self.node1.id)
        self.assertEqual(len(self.store.nodes), 1)
        self.assertIsNone(self.store.get_node(self.node1.id))
        self.assertEqual(self.store.get_node(self.node2.id), self.node2)
    
    def test_remove_nonexistent_node_raises_error(self):
        """Test that removing non-existent node raises error."""
        with self.assertRaises(ValueError):
            self.store.remove_node("nonexistent")
    
    def test_entrance_and_exit_nodes(self):
        """Test setting and getting entrance/exit nodes."""
        self.store.add_node(self.node1)
        self.store.add_node(self.node2)
        
        self.store.entrance_node_id = self.node1.id
        self.store.exit_node_id = self.node2.id
        
        self.assertEqual(self.store.get_entrance_node(), self.node1)
        self.assertEqual(self.store.get_exit_node(), self.node2)
    
    def test_find_nodes_by_aisle(self):
        """Test finding nodes by aisle number."""
        node_aisle_5 = AisleNode(name="Aisle 5", aisle_number=5)
        node_aisle_6 = AisleNode(name="Aisle 6", aisle_number=6)
        node_aisle_5_2 = AisleNode(name="Aisle 5 End", aisle_number=5)
        
        self.store.add_node(node_aisle_5)
        self.store.add_node(node_aisle_6)
        self.store.add_node(node_aisle_5_2)
        
        aisle_5_nodes = self.store.find_nodes_by_aisle(5)
        self.assertEqual(len(aisle_5_nodes), 2)
        self.assertIn(node_aisle_5, aisle_5_nodes)
        self.assertIn(node_aisle_5_2, aisle_5_nodes)
    
    def test_bounds_calculation(self):
        """Test store bounds calculation."""
        # Empty store should have zero bounds
        empty_store = Store()
        self.assertEqual(empty_store.bounds, (0.0, 0.0, 0.0, 0.0))
        
        # Store with nodes should calculate correct bounds
        self.store.add_node(AisleNode(x=10, y=5))
        self.store.add_node(AisleNode(x=2, y=15))
        self.store.add_node(AisleNode(x=8, y=3))
        
        bounds = self.store.bounds
        self.assertEqual(bounds, (2, 3, 10, 15))  # min_x, min_y, max_x, max_y


class TestItem(unittest.TestCase):
    """Test the Item class."""
    
    def test_valid_item_creation(self):
        """Test creating a valid item."""
        item = Item(
            name="Test Item",
            aisle_node_id="node123",
            sub_section=SubSection.LEFT,
            category="Test Category",
            price=5.99,
            quantity_needed=2
        )
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.aisle_node_id, "node123")
        self.assertEqual(item.sub_section, SubSection.LEFT)
        self.assertEqual(item.price, 5.99)
        self.assertEqual(item.quantity_needed, 2)
    
    def test_invalid_item_creation(self):
        """Test that invalid items raise ValueError."""
        # Empty name
        with self.assertRaises(ValueError):
            Item(name="", aisle_node_id="node123")
        
        # Empty aisle node ID
        with self.assertRaises(ValueError):
            Item(name="Test", aisle_node_id="")
        
        # Negative quantity
        with self.assertRaises(ValueError):
            Item(name="Test", aisle_node_id="node123", quantity_needed=0)
        
        # Negative price
        with self.assertRaises(ValueError):
            Item(name="Test", aisle_node_id="node123", price=-1.0)
    
    def test_location_description(self):
        """Test getting location description."""
        store = Store()
        node = AisleNode(name="Produce", aisle_number=1)
        store.add_node(node)
        
        item = Item(
            name="Bananas",
            aisle_node_id=node.id,
            sub_section=SubSection.LEFT
        )
        
        description = item.get_location_description(store)
        self.assertEqual(description, "Aisle 1 (Left)")
    
    def test_is_at_node(self):
        """Test checking if item is at a specific node."""
        item = Item(name="Test", aisle_node_id="node123")
        self.assertTrue(item.is_at_node("node123"))
        self.assertFalse(item.is_at_node("node456"))


class TestShoppingList(unittest.TestCase):
    """Test the ShoppingList class."""
    
    def setUp(self):
        """Set up test shopping list with sample items."""
        self.shopping_list = ShoppingList(name="Test List")
        self.item1 = Item(name="Item 1", aisle_node_id="node1", price=2.50)
        self.item2 = Item(name="Item 2", aisle_node_id="node2", price=3.75, quantity_needed=2)
        self.item3 = Item(name="Item 3", aisle_node_id="node1")  # No price
    
    def test_add_and_remove_items(self):
        """Test adding and removing items from shopping list."""
        self.shopping_list.add_item(self.item1)
        self.shopping_list.add_item(self.item2)
        
        self.assertEqual(len(self.shopping_list.items), 2)
        
        self.shopping_list.remove_item(self.item1.id)
        self.assertEqual(len(self.shopping_list.items), 1)
        self.assertEqual(self.shopping_list.items[0], self.item2)
    
    def test_get_required_nodes(self):
        """Test getting set of required node IDs."""
        self.shopping_list.add_item(self.item1)
        self.shopping_list.add_item(self.item2)
        self.shopping_list.add_item(self.item3)
        
        required = self.shopping_list.get_required_nodes()
        self.assertEqual(required, {"node1", "node2"})
    
    def test_get_items_at_node(self):
        """Test getting items at a specific node."""
        self.shopping_list.add_item(self.item1)
        self.shopping_list.add_item(self.item2)
        self.shopping_list.add_item(self.item3)
        
        items_at_node1 = self.shopping_list.get_items_at_node("node1")
        self.assertEqual(len(items_at_node1), 2)
        self.assertIn(self.item1, items_at_node1)
        self.assertIn(self.item3, items_at_node1)
    
    def test_group_by_node(self):
        """Test grouping items by node."""
        self.shopping_list.add_item(self.item1)
        self.shopping_list.add_item(self.item2)
        self.shopping_list.add_item(self.item3)
        
        grouped = self.shopping_list.group_by_node()
        self.assertEqual(len(grouped), 2)
        self.assertEqual(len(grouped["node1"]), 2)
        self.assertEqual(len(grouped["node2"]), 1)
    
    def test_total_items_count(self):
        """Test calculating total item count considering quantities."""
        self.shopping_list.add_item(self.item1)  # quantity 1
        self.shopping_list.add_item(self.item2)  # quantity 2
        
        total = self.shopping_list.total_items_count()
        self.assertEqual(total, 3)
    
    def test_total_estimated_cost(self):
        """Test calculating total estimated cost."""
        self.shopping_list.add_item(self.item1)  # $2.50 x 1 = $2.50
        self.shopping_list.add_item(self.item2)  # $3.75 x 2 = $7.50
        self.shopping_list.add_item(self.item3)  # No price
        
        total = self.shopping_list.total_estimated_cost()
        self.assertEqual(total, 10.00)  # $2.50 + $7.50


class TestRouteOptimization(unittest.TestCase):
    """Test route optimization algorithms."""
    
    def setUp(self):
        """Set up test store and shopping list."""
        self.store = Store()
        
        # Create simple linear layout for predictable results
        self.entrance = AisleNode(name="Entrance", x=0, y=0)
        self.node1 = AisleNode(name="Node 1", x=10, y=0)
        self.node2 = AisleNode(name="Node 2", x=20, y=0)
        self.node3 = AisleNode(name="Node 3", x=30, y=0)
        self.exit = AisleNode(name="Exit", x=40, y=0)
        
        for node in [self.entrance, self.node1, self.node2, self.node3, self.exit]:
            self.store.add_node(node)
        
        self.store.entrance_node_id = self.entrance.id
        self.store.exit_node_id = self.exit.id
        
        # Create shopping list
        self.shopping_list = ShoppingList()
        self.shopping_list.add_item(Item(name="Item 1", aisle_node_id=self.node1.id))
        self.shopping_list.add_item(Item(name="Item 2", aisle_node_id=self.node2.id))
        self.shopping_list.add_item(Item(name="Item 3", aisle_node_id=self.node3.id))
    
    def test_greedy_optimizer(self):
        """Test the greedy optimizer."""
        optimizer = get_optimizer('greedy', self.store)
        route = optimizer.optimize_route(self.shopping_list)
        
        self.assertIsInstance(route, Route)
        self.assertEqual(len(route.nodes), 5)  # entrance + 3 items + exit
        self.assertEqual(route.nodes[0], self.entrance)
        self.assertEqual(route.nodes[-1], self.exit)
        self.assertGreater(route.total_distance, 0)
    
    def test_brute_force_optimizer(self):
        """Test the brute force optimizer."""
        optimizer = get_optimizer('brute_force', self.store)
        route = optimizer.optimize_route(self.shopping_list)
        
        self.assertIsInstance(route, Route)
        self.assertEqual(len(route.nodes), 5)
        self.assertEqual(route.nodes[0], self.entrance)
        self.assertEqual(route.nodes[-1], self.exit)
    
    def test_two_opt_optimizer(self):
        """Test the 2-opt optimizer."""
        optimizer = get_optimizer('two_opt', self.store)
        route = optimizer.optimize_route(self.shopping_list)
        
        self.assertIsInstance(route, Route)
        self.assertEqual(len(route.nodes), 5)
        self.assertEqual(route.nodes[0], self.entrance)
        self.assertEqual(route.nodes[-1], self.exit)
    
    def test_invalid_algorithm_raises_error(self):
        """Test that invalid algorithm name raises error."""
        with self.assertRaises(ValueError):
            get_optimizer('invalid_algorithm', self.store)
    
    def test_empty_shopping_list_raises_error(self):
        """Test that empty shopping list raises error."""
        optimizer = get_optimizer('greedy', self.store)
        empty_list = ShoppingList()
        
        with self.assertRaises(ValueError):
            optimizer.optimize_route(empty_list)


if __name__ == '__main__':
    unittest.main()