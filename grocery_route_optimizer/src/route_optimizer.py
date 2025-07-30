"""
Route optimizer module to calculate the optimal shopping path
"""

import networkx as nx
from python_tsp import tsp
import numpy as np
import re
from collections import defaultdict


class RouteOptimizer:
    """Class to optimize shopping routes through grocery stores"""
    
    def __init__(self):
        # Define typical grocery store layout
        self.store_layout = self._create_store_layout()
        
    def _create_store_layout(self):
        """
        Create a graph representing typical grocery store layout
        
        Returns a dictionary mapping locations to (x, y) coordinates
        """
        layout = {
            # Entry/Exit
            'Entrance': (0, 0),
            'Checkout': (0, 1),
            
            # Perimeter departments (typically around the edges)
            'Produce Section': (1, 10),
            'Meat Department': (10, 10),
            'Seafood Department': (11, 10),
            'Deli Department': (12, 10),
            'Bakery Section': (13, 10),
            'Frozen Foods': (14, 5),
            
            # Aisles (in the middle)
            'Aisle 1 - Dairy': (2, 8),
            'Aisle 2 - Eggs': (3, 8),
            'Aisle 3 - General Grocery': (4, 8),
            'Aisle 4 - Breakfast': (5, 8),
            'Aisle 5 - Grains & Pasta': (6, 8),
            'Aisle 6 - Baking': (7, 8),
            'Aisle 7 - Canned Goods': (8, 8),
            'Aisle 8 - Snacks': (9, 8),
            'Aisle 9 - Coffee & Tea': (10, 8),
            'Aisle 10 - Beverages': (11, 8),
            'Aisle 11 - Cooking Oils': (12, 8),
            'Aisle 11 - Spices': (12, 7),
            'Aisle 12 - Condiments': (13, 8),
        }
        
        return layout
        
    def optimize_route(self, items_with_locations):
        """
        Optimize the shopping route using TSP algorithm
        
        Args:
            items_with_locations: List of tuples (item_name, location)
            
        Returns:
            Ordered list of tuples (item_name, location) representing optimal path
        """
        # Extract unique locations
        locations = []
        location_to_items = defaultdict(list)
        
        for item, location in items_with_locations:
            location_to_items[location].append(item)
            if location not in locations:
                locations.append(location)
                
        # Always start at entrance and end at checkout
        all_locations = ['Entrance'] + locations + ['Checkout']
        
        # Get coordinates for each location
        coordinates = []
        valid_locations = []
        
        for loc in all_locations:
            coord = self._get_location_coordinates(loc)
            if coord:
                coordinates.append(coord)
                valid_locations.append(loc)
                
        if len(coordinates) < 3:
            # Not enough locations for optimization
            return items_with_locations
            
        # Create distance matrix
        n = len(coordinates)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Manhattan distance (more realistic for store aisles)
                    distance_matrix[i][j] = self._manhattan_distance(
                        coordinates[i], coordinates[j]
                    )
                    
        # Solve TSP
        try:
            # Use nearest neighbor heuristic for speed
            path = self._nearest_neighbor_tsp(distance_matrix)
        except:
            # Fallback to simple ordering
            path = list(range(n))
            
        # Convert path back to items
        optimized_route = []
        
        for idx in path[1:-1]:  # Skip entrance and checkout
            location = valid_locations[idx]
            # Add all items at this location
            for item in location_to_items[location]:
                optimized_route.append((item, location))
                
        return optimized_route
        
    def _get_location_coordinates(self, location):
        """Get coordinates for a location"""
        # Check exact match first
        if location in self.store_layout:
            return self.store_layout[location]
            
        # Try to match by aisle number
        aisle_match = re.search(r'Aisle (\d+)', location)
        if aisle_match:
            aisle_num = int(aisle_match.group(1))
            # Look for any aisle with this number
            for loc, coord in self.store_layout.items():
                if f'Aisle {aisle_num}' in loc:
                    return coord
                    
        # Try partial matching
        location_lower = location.lower()
        for loc, coord in self.store_layout.items():
            if location_lower in loc.lower() or loc.lower() in location_lower:
                return coord
                
        # Default to middle of store
        return (7, 5)
        
    def _manhattan_distance(self, coord1, coord2):
        """Calculate Manhattan distance between two coordinates"""
        return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])
        
    def _nearest_neighbor_tsp(self, distance_matrix):
        """
        Solve TSP using nearest neighbor heuristic
        
        Args:
            distance_matrix: NxN numpy array of distances
            
        Returns:
            List of indices representing the path
        """
        n = len(distance_matrix)
        unvisited = set(range(1, n))  # Start from 0 (entrance)
        path = [0]
        current = 0
        
        # Build path
        while unvisited:
            # Find nearest unvisited location
            nearest = None
            nearest_dist = float('inf')
            
            for next_loc in unvisited:
                dist = distance_matrix[current][next_loc]
                if dist < nearest_dist:
                    nearest = next_loc
                    nearest_dist = dist
                    
            if nearest is not None:
                path.append(nearest)
                unvisited.remove(nearest)
                current = nearest
                
        # Return to start (checkout is at index n-1)
        if len(path) > 1:
            path.append(n - 1)
            
        return path
        
    def get_route_distance(self, route):
        """Calculate total distance for a route"""
        total_distance = 0
        
        # Add entrance
        locations = ['Entrance'] + [loc for _, loc in route] + ['Checkout']
        
        for i in range(len(locations) - 1):
            coord1 = self._get_location_coordinates(locations[i])
            coord2 = self._get_location_coordinates(locations[i + 1])
            if coord1 and coord2:
                total_distance += self._manhattan_distance(coord1, coord2)
                
        return total_distance
        
    def group_items_by_location(self, items_with_locations):
        """Group items that are in the same location"""
        location_groups = defaultdict(list)
        
        for item, location in items_with_locations:
            location_groups[location].append(item)
            
        return dict(location_groups)