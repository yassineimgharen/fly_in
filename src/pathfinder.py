"""Pathfinder for drone routing system."""
from models import Graph, Zone


class Pathfinder:
    """Finds paths through the drone network."""

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the Pathfinder.
        graph: The drone network graph
        """
        self.graph = graph

    def find_path(self, start: Zone, end: Zone) -> list[Zone]:
        """Find shortest path considering zone costs and priority."""
        queue = [(start, 0)]  # (zone, cost)
        came_from: dict[Zone, Zone | None] = {start: None}
        cost_to: dict[Zone, int] = {start: 0}

        while queue:
            current, _ = queue.pop(0)

            if current == end:
                return self._reconstruct_path(came_from, end)

            for neighbor in self.graph.get_neighbors(current):
                if neighbor.is_blocked():
                    continue
                
                new_cost = cost_to[current] + neighbor.cost
                
                if neighbor not in cost_to or new_cost < cost_to[neighbor]:
                    cost_to[neighbor] = new_cost
                    came_from[neighbor] = current
                    queue.append((neighbor, new_cost))
                    # Sort by cost, then prefer priority zones
                    queue.sort(key=lambda x: (cost_to[x[0]], 0 if x[0].zone_type == 'priority' else 1))

        return []
    def _reconstruct_path(
        self,
        came_from: dict[Zone, Zone | None],
        end: Zone
    ) -> list[Zone]:
        """
        Reconstruct path from came_from dictionary.
        return List of zones from start to end
        """
        path = []
        current: Zone | None = end

        while current is not None:
            path.append(current)
            current = came_from[current]

        path.reverse()
        return path

    def find_multiple_paths(self, k: int) -> list[list[Zone]]:
        """
        Find K different paths using BFS with zone exclusion.
        Returns list of diverse paths.
        """
        paths = []
        # paths = [[start, junction, path_a, goal]]

        # Find first path
        first_path = self.find_path(self.graph.start_zone, self.graph.end_zone)

        if not first_path:
            return []

        paths.append(first_path)

        # Try to find alternative paths by excluding zones from previous paths
        for zone in first_path[1:-1]: # Exclude middle zones only
            if len(paths) >= k:
                break

            # Try excluding this zone
            alt_path = self._find_path_excluding_set({zone})

            # Check if path is different from all existing paths
            if alt_path and not self._path_exists(alt_path, paths):
                paths.append(alt_path)

        # If we still need more paths, try excluding combinations
        if len(paths) < k and len(first_path) > 3:
            for i in range(1, len(first_path) - 2):
                for j in range(i + 1, len(first_path) - 1):
                    if len(paths) >= k:
                        break

                    # Exclude two zones
                    excluded = {first_path[i], first_path[j]}
                    alt_path = self._find_path_excluding_set(excluded)

                    if alt_path and not self._path_exists(alt_path, paths):
                        paths.append(alt_path)

        # Fill remaining with first path if needed
        while len(paths) < k:
            paths.append(first_path)
        
        return paths[:k]

    def _find_path_excluding_set(self, exclude: set[Zone]) -> list[Zone]:
        """Find path using BFS while excluding a set of zones."""
        queue = [self.graph.start_zone]
        visited = {self.graph.start_zone}
        came_from: dict[Zone, Zone | None] = {self.graph.start_zone: None}

        while queue:
            current = queue.pop(0)

            if current == self.graph.end_zone:
                return self._reconstruct_path(came_from, self.graph.end_zone)

            for neighbor in self.graph.get_neighbors(current):
                if (neighbor not in visited and
                    not neighbor.is_blocked() and
                    neighbor not in exclude):
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)

        return []

    def _path_exists(self, path: list[Zone], paths: list[list[Zone]]) -> bool:
        """Check if path already exists in paths list."""
        path_tuple = tuple(zone.name for zone in path)
        for existing in paths:
            existing_tuple = tuple(zone.name for zone in existing)
            if path_tuple == existing_tuple:
                return True
        return False
