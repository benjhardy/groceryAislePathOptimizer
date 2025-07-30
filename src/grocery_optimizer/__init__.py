"""
Grocery Route Optimizer - Core data model and routing algorithms.

This package provides the core data structures and algorithms for optimizing
grocery shopping routes within stores.
"""

from .models import AisleNode, Store, Item, ShoppingList, SubSection
from .routing import RouteOptimizer, Route, get_optimizer

__version__ = "0.1.0"
__all__ = ["AisleNode", "Store", "Item", "ShoppingList", "SubSection", 
           "RouteOptimizer", "Route", "get_optimizer"]