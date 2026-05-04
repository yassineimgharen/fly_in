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
        """
        Find shortest path from start to end using BFS.
        Returns:
            List of zones representing the path, empty if no path found
        """
        queue = [start]
        visited = {start}
        came_from: dict[Zone, Zone | None] = {start: None}

        while queue:
            current = queue.pop(0)

            if current == end:
                return self._reconstruct_path(came_from, end)

            neighbors = self.graph.get_neighbors(current)
            neighbors = self._sort_by_priority(neighbors)

            for neighbor in neighbors:
                if neighbor not in visited and not neighbor.is_blocked():
                    visited.add(neighbor)
                    came_from[neighbor] = current
                    queue.append(neighbor)
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

        first_path = self.find_path(self.graph.start_zone, self.graph.end_zone)
        if not first_path:
            return []

        paths.append(first_path)

        # Try to find alternative paths by excluding zones from previous paths
        for zone in first_path[1:-1]:  # Exclude middle zones only
            if len(paths) >= k:
                break

            alt_path = self._find_path_excluding_set({zone})
            if alt_path and not self._path_exists(alt_path, paths):
                paths.append(alt_path)

        # Fill remaining with round robin distribution across found paths
        path_count = len(paths)
        while len(paths) < k:
            idx = len(paths) % path_count
            paths.append(paths[idx])

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

    def _sort_by_priority(self, zones: list[Zone]) -> list[Zone]:
        """
        Sort zones to prefer priority zones first.
        Args:
            zones: List of zones to sort
            Sorted list with priority zones first
        """
        priority_zones = [z for z in zones if z.zone_type == "priority"]
        other_zones = [z for z in zones if z.zone_type != "priority"]
        return priority_zones + other_zones
