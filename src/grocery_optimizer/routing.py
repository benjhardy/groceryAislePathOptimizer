"""
Route optimization algorithms for grocery shopping.

This module implements various algorithms for solving the traveling salesman
problem and finding optimal paths through a store's aisle nodes.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Set
import itertools
from abc import ABC, abstractmethod
import math

from .models import AisleNode, Store, ShoppingList


@dataclass
class Route:
    """
    Represents an optimized route through the store.
    
    Contains the sequence of nodes to visit and metadata about the route.
    """
    
    nodes: List[AisleNode]
    total_distance: float
    estimated_time_minutes: Optional[float] = None
    
    @property
    def node_ids(self) -> List[str]:
        """Get list of node IDs in the route."""
        return [node.id for node in self.nodes]
    
    def get_segments(self) -> List[Tuple[AisleNode, AisleNode]]:
        """Get list of route segments as (from_node, to_node) pairs."""
        if len(self.nodes) < 2:
            return []
        return [(self.nodes[i], self.nodes[i + 1]) for i in range(len(self.nodes) - 1)]


class RouteOptimizer(ABC):
    """
    Abstract base class for route optimization algorithms.
    
    Defines the interface for different TSP solving approaches.
    """
    
    def __init__(self, store: Store):
        """Initialize with a store instance."""
        self.store = store
        self._distance_cache: Dict[Tuple[str, str], float] = {}
    
    def get_distance(self, node1: AisleNode, node2: AisleNode) -> float:
        """
        Get distance between two nodes with caching.
        
        Uses Euclidean distance by default. Override for custom distance metrics.
        """
        cache_key = (node1.id, node2.id)
        if cache_key in self._distance_cache:
            return self._distance_cache[cache_key]
        
        distance = node1.distance_to(node2)
        self._distance_cache[cache_key] = distance
        # Cache both directions for symmetric distance
        self._distance_cache[(node2.id, node1.id)] = distance
        return distance
    
    @abstractmethod
    def optimize_route(self, shopping_list: ShoppingList, 
                      start_node: Optional[AisleNode] = None,
                      end_node: Optional[AisleNode] = None) -> Route:
        """
        Find the optimal route for the given shopping list.
        
        Args:
            shopping_list: List of items to collect
            start_node: Starting location (default: store entrance)
            end_node: Ending location (default: store exit)
            
        Returns:
            Optimized route through the required nodes
        """
        pass
    
    def _get_start_node(self, start_node: Optional[AisleNode]) -> AisleNode:
        """Get the starting node, using store entrance as default."""
        if start_node:
            return start_node
        
        entrance = self.store.get_entrance_node()
        if entrance:
            return entrance
        
        # Fallback to first node if no entrance defined
        if self.store.nodes:
            return self.store.nodes[0]
        
        raise ValueError("No start node available and store has no nodes")
    
    def _get_end_node(self, end_node: Optional[AisleNode]) -> AisleNode:
        """Get the ending node, using store exit as default."""
        if end_node:
            return end_node
        
        exit_node = self.store.get_exit_node()
        if exit_node:
            return exit_node
        
        # Use entrance as exit if no exit defined
        entrance = self.store.get_entrance_node()
        if entrance:
            return entrance
        
        # Fallback to first node
        if self.store.nodes:
            return self.store.nodes[0]
        
        raise ValueError("No end node available and store has no nodes")


class BruteForceOptimizer(RouteOptimizer):
    """
    Brute force TSP solver that tries all possible permutations.
    
    Only suitable for small numbers of nodes (< 10) due to factorial complexity.
    """
    
    def optimize_route(self, shopping_list: ShoppingList, 
                      start_node: Optional[AisleNode] = None,
                      end_node: Optional[AisleNode] = None) -> Route:
        """
        Find optimal route using brute force enumeration.
        
        Tries all possible permutations of required nodes.
        """
        required_node_ids = shopping_list.get_required_nodes()
        if not required_node_ids:
            raise ValueError("Shopping list contains no items")
        
        # Get required nodes
        required_nodes = []
        for node_id in required_node_ids:
            node = self.store.get_node(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found in store")
            required_nodes.append(node)
        
        # Warn if too many nodes for brute force
        if len(required_nodes) > 10:
            raise ValueError(f"Too many nodes ({len(required_nodes)}) for brute force optimization")
        
        start = self._get_start_node(start_node)
        end = self._get_end_node(end_node)
        
        # If start and end are the same and not in required nodes, just solve TSP
        if start.id == end.id and start.id not in required_node_ids:
            return self._solve_tsp_circuit(required_nodes, start)
        
        # Otherwise solve as a path problem
        return self._solve_tsp_path(required_nodes, start, end)
    
    def _solve_tsp_circuit(self, nodes: List[AisleNode], start: AisleNode) -> Route:
        """Solve TSP where we return to the starting point."""
        if not nodes:
            return Route(nodes=[start], total_distance=0.0)
        
        best_distance = float('inf')
        best_route = None
        
        # Try all permutations
        for perm in itertools.permutations(nodes):
            route_nodes = [start] + list(perm) + [start]
            distance = self._calculate_route_distance(route_nodes)
            
            if distance < best_distance:
                best_distance = distance
                best_route = route_nodes
        
        return Route(nodes=best_route, total_distance=best_distance)
    
    def _solve_tsp_path(self, nodes: List[AisleNode], start: AisleNode, end: AisleNode) -> Route:
        """Solve TSP as a path from start to end."""
        if not nodes:
            route_nodes = [start, end] if start.id != end.id else [start]
            distance = self.get_distance(start, end) if start.id != end.id else 0.0
            return Route(nodes=route_nodes, total_distance=distance)
        
        # Remove start and end from nodes if they're included
        nodes_to_visit = [n for n in nodes if n.id not in (start.id, end.id)]
        
        if not nodes_to_visit:
            route_nodes = [start, end] if start.id != end.id else [start]
            distance = self.get_distance(start, end) if start.id != end.id else 0.0
            return Route(nodes=route_nodes, total_distance=distance)
        
        best_distance = float('inf')
        best_route = None
        
        # Try all permutations of intermediate nodes
        for perm in itertools.permutations(nodes_to_visit):
            route_nodes = [start] + list(perm) + ([end] if start.id != end.id else [])
            distance = self._calculate_route_distance(route_nodes)
            
            if distance < best_distance:
                best_distance = distance
                best_route = route_nodes
        
        return Route(nodes=best_route, total_distance=best_distance)
    
    def _calculate_route_distance(self, nodes: List[AisleNode]) -> float:
        """Calculate total distance for a route."""
        if len(nodes) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(nodes) - 1):
            total += self.get_distance(nodes[i], nodes[i + 1])
        return total


class GreedyOptimizer(RouteOptimizer):
    """
    Greedy nearest-neighbor TSP solver.
    
    Fast heuristic that always moves to the nearest unvisited node.
    Not optimal but scales well for larger problems.
    """
    
    def optimize_route(self, shopping_list: ShoppingList, 
                      start_node: Optional[AisleNode] = None,
                      end_node: Optional[AisleNode] = None) -> Route:
        """
        Find route using greedy nearest-neighbor heuristic.
        """
        required_node_ids = shopping_list.get_required_nodes()
        if not required_node_ids:
            raise ValueError("Shopping list contains no items")
        
        # Get required nodes
        required_nodes = []
        for node_id in required_node_ids:
            node = self.store.get_node(node_id)
            if not node:
                raise ValueError(f"Node {node_id} not found in store")
            required_nodes.append(node)
        
        start = self._get_start_node(start_node)
        end = self._get_end_node(end_node)
        
        return self._greedy_path(required_nodes, start, end)
    
    def _greedy_path(self, nodes: List[AisleNode], start: AisleNode, end: AisleNode) -> Route:
        """Build path using greedy nearest-neighbor approach."""
        unvisited = set(node.id for node in nodes if node.id not in (start.id, end.id))
        route = [start]
        current = start
        total_distance = 0.0
        
        # Visit all required nodes using nearest neighbor
        while unvisited:
            nearest_node = None
            nearest_distance = float('inf')
            
            for node in nodes:
                if node.id in unvisited:
                    distance = self.get_distance(current, node)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_node = node
            
            if nearest_node:
                route.append(nearest_node)
                total_distance += nearest_distance
                current = nearest_node
                unvisited.remove(nearest_node.id)
        
        # Add end node if different from start
        if start.id != end.id:
            route.append(end)
            total_distance += self.get_distance(current, end)
        
        return Route(nodes=route, total_distance=total_distance)


class TwoOptOptimizer(RouteOptimizer):
    """
    2-opt local search improvement for TSP.
    
    Starts with a greedy solution and improves it using 2-opt swaps.
    Balances solution quality with computation time.
    """
    
    def __init__(self, store: Store, max_iterations: int = 1000):
        """Initialize with maximum number of improvement iterations."""
        super().__init__(store)
        self.max_iterations = max_iterations
    
    def optimize_route(self, shopping_list: ShoppingList, 
                      start_node: Optional[AisleNode] = None,
                      end_node: Optional[AisleNode] = None) -> Route:
        """
        Find route using greedy initialization + 2-opt improvement.
        """
        # Start with greedy solution
        greedy_optimizer = GreedyOptimizer(self.store)
        initial_route = greedy_optimizer.optimize_route(shopping_list, start_node, end_node)
        
        # Improve with 2-opt
        improved_route = self._two_opt_improve(initial_route)
        return improved_route
    
    def _two_opt_improve(self, route: Route) -> Route:
        """Improve route using 2-opt local search."""
        if len(route.nodes) < 4:
            return route  # Cannot improve routes with < 4 nodes
        
        current_nodes = route.nodes[:]
        current_distance = route.total_distance
        
        for iteration in range(self.max_iterations):
            improved = False
            
            # Try all possible 2-opt swaps
            for i in range(1, len(current_nodes) - 2):
                for j in range(i + 1, len(current_nodes) - 1):
                    # Create new route by reversing segment between i and j
                    new_nodes = (current_nodes[:i] + 
                                current_nodes[i:j+1][::-1] + 
                                current_nodes[j+1:])
                    
                    new_distance = self._calculate_route_distance(new_nodes)
                    
                    if new_distance < current_distance:
                        current_nodes = new_nodes
                        current_distance = new_distance
                        improved = True
                        break
                
                if improved:
                    break
            
            if not improved:
                break  # No improvement found, stop
        
        return Route(nodes=current_nodes, total_distance=current_distance)
    
    def _calculate_route_distance(self, nodes: List[AisleNode]) -> float:
        """Calculate total distance for a route."""
        if len(nodes) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(nodes) - 1):
            total += self.get_distance(nodes[i], nodes[i + 1])
        return total


# Factory function for getting optimizers
def get_optimizer(algorithm: str, store: Store, **kwargs) -> RouteOptimizer:
    """
    Factory function to create route optimizers.
    
    Args:
        algorithm: 'brute_force', 'greedy', or 'two_opt'
        store: Store instance
        **kwargs: Additional parameters for specific optimizers
        
    Returns:
        RouteOptimizer instance
    """
    if algorithm == 'brute_force':
        return BruteForceOptimizer(store)
    elif algorithm == 'greedy':
        return GreedyOptimizer(store)
    elif algorithm == 'two_opt':
        max_iterations = kwargs.get('max_iterations', 1000)
        return TwoOptOptimizer(store, max_iterations)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. "
                        "Choose from: brute_force, greedy, two_opt")