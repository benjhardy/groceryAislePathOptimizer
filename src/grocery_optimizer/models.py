"""
Core data models for the grocery route optimizer.

This module defines the fundamental data structures for representing stores,
aisles, and items in the grocery routing system.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Set
from enum import Enum
import uuid


class SubSection(Enum):
    """Enumeration of possible sub-sections within an aisle."""
    LEFT = "Left"
    RIGHT = "Right"
    CENTER = "Center"
    END_CAP = "End-cap"
    TOP_SHELF = "Top-shelf"
    BOTTOM_SHELF = "Bottom-shelf"


@dataclass(frozen=True)
class AisleNode:
    """
    Represents a specific location within a store with coordinates.
    
    This class models physical locations in the store that can be visited
    during shopping. Each node has a unique identifier and x,y coordinates
    for pathfinding algorithms.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    x: float = 0.0
    y: float = 0.0
    aisle_number: Optional[int] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Validate coordinates are non-negative."""
        if self.x < 0 or self.y < 0:
            raise ValueError("Coordinates must be non-negative")
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        """Return coordinates as a tuple."""
        return (self.x, self.y)
    
    def distance_to(self, other: 'AisleNode') -> float:
        """Calculate Euclidean distance to another aisle node."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def manhattan_distance_to(self, other: 'AisleNode') -> float:
        """Calculate Manhattan distance to another aisle node."""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class Store:
    """
    Represents a physical store with a collection of aisle nodes.
    
    The store maintains a graph of navigable locations and provides
    methods for finding nodes and calculating distances between them.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    address: str = ""
    nodes: List[AisleNode] = field(default_factory=list)
    entrance_node_id: Optional[str] = None
    exit_node_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize node lookup dictionary."""
        self._node_lookup: Dict[str, AisleNode] = {}
        self._update_node_lookup()
    
    def _update_node_lookup(self):
        """Update internal node lookup dictionary."""
        self._node_lookup = {node.id: node for node in self.nodes}
    
    def add_node(self, node: AisleNode) -> None:
        """Add a new aisle node to the store."""
        if node.id in self._node_lookup:
            raise ValueError(f"Node with id {node.id} already exists")
        self.nodes.append(node)
        self._node_lookup[node.id] = node
    
    def remove_node(self, node_id: str) -> None:
        """Remove an aisle node from the store."""
        if node_id not in self._node_lookup:
            raise ValueError(f"Node with id {node_id} not found")
        
        # Remove from nodes list
        self.nodes = [node for node in self.nodes if node.id != node_id]
        # Remove from lookup
        del self._node_lookup[node_id]
        
        # Clear entrance/exit if they reference removed node
        if self.entrance_node_id == node_id:
            self.entrance_node_id = None
        if self.exit_node_id == node_id:
            self.exit_node_id = None
    
    def get_node(self, node_id: str) -> Optional[AisleNode]:
        """Get a node by its ID."""
        return self._node_lookup.get(node_id)
    
    def get_entrance_node(self) -> Optional[AisleNode]:
        """Get the entrance node if set."""
        if self.entrance_node_id:
            return self.get_node(self.entrance_node_id)
        return None
    
    def get_exit_node(self) -> Optional[AisleNode]:
        """Get the exit node if set."""
        if self.exit_node_id:
            return self.get_node(self.exit_node_id)
        return None
    
    def find_nodes_by_aisle(self, aisle_number: int) -> List[AisleNode]:
        """Find all nodes in a specific aisle."""
        return [node for node in self.nodes if node.aisle_number == aisle_number]
    
    def get_all_coordinates(self) -> List[Tuple[float, float]]:
        """Get coordinates of all nodes as a list of tuples."""
        return [node.coordinates for node in self.nodes]
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """Get the bounding box of the store (min_x, min_y, max_x, max_y)."""
        if not self.nodes:
            return (0.0, 0.0, 0.0, 0.0)
        
        xs = [node.x for node in self.nodes]
        ys = [node.y for node in self.nodes]
        return (min(xs), min(ys), max(xs), max(ys))


@dataclass
class Item:
    """
    Represents a grocery item with its location within the store.
    
    Items are associated with specific aisle nodes and can have optional
    sub-sections for more precise location information.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    aisle_node_id: str = ""
    sub_section: Optional[SubSection] = None
    category: str = ""
    barcode: Optional[str] = None
    price: Optional[float] = None
    quantity_needed: int = 1
    
    def __post_init__(self):
        """Validate item data."""
        if not self.name.strip():
            raise ValueError("Item name cannot be empty")
        if not self.aisle_node_id.strip():
            raise ValueError("Aisle node ID cannot be empty")
        if self.quantity_needed <= 0:
            raise ValueError("Quantity needed must be positive")
        if self.price is not None and self.price < 0:
            raise ValueError("Price cannot be negative")
    
    def get_location_description(self, store: Store) -> str:
        """Get a human-readable description of the item's location."""
        node = store.get_node(self.aisle_node_id)
        if not node:
            return "Unknown location"
        
        location = node.name or f"Node {node.id[:8]}"
        if node.aisle_number:
            location = f"Aisle {node.aisle_number}"
        
        if self.sub_section:
            location += f" ({self.sub_section.value})"
        
        return location
    
    def is_at_node(self, node_id: str) -> bool:
        """Check if this item is located at the specified node."""
        return self.aisle_node_id == node_id


@dataclass
class ShoppingList:
    """
    Represents a collection of items to be collected during shopping.
    
    This class manages the list of items and provides methods for
    organizing and analyzing the shopping requirements.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Shopping List"
    items: List[Item] = field(default_factory=list)
    created_at: Optional[str] = None
    
    def add_item(self, item: Item) -> None:
        """Add an item to the shopping list."""
        self.items.append(item)
    
    def remove_item(self, item_id: str) -> None:
        """Remove an item from the shopping list."""
        self.items = [item for item in self.items if item.id != item_id]
    
    def get_required_nodes(self) -> Set[str]:
        """Get the set of node IDs that need to be visited."""
        return {item.aisle_node_id for item in self.items}
    
    def get_items_at_node(self, node_id: str) -> List[Item]:
        """Get all items located at a specific node."""
        return [item for item in self.items if item.aisle_node_id == node_id]
    
    def group_by_node(self) -> Dict[str, List[Item]]:
        """Group items by their aisle node ID."""
        groups = {}
        for item in self.items:
            if item.aisle_node_id not in groups:
                groups[item.aisle_node_id] = []
            groups[item.aisle_node_id].append(item)
        return groups
    
    def total_items_count(self) -> int:
        """Get the total number of individual items (considering quantities)."""
        return sum(item.quantity_needed for item in self.items)
    
    def total_estimated_cost(self) -> Optional[float]:
        """Calculate total estimated cost if prices are available."""
        total = 0.0
        has_prices = False
        
        for item in self.items:
            if item.price is not None:
                total += item.price * item.quantity_needed
                has_prices = True
        
        return total if has_prices else None