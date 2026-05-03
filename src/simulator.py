"""Simulator for drone routing system."""

from models import Graph, Drone, Zone


class Simulator:
    """Simulates drone movements turn by turn."""

    def __init__(self, graph: Graph, paths: list[list[Zone]]) -> None:
        """Initialize the Simulator."""
        self.graph = graph
        self.paths = paths
        self.turn = 0

        self.drones = [Drone(i + 1) for i in range(graph.nb_drones)]

        self.drone_positions: dict[Drone, Zone] = {}

        # Track progress in path for each drone
        self.path_index: dict[Drone, int] = {}

        # Track drones in transit to restricted zones
        self.in_transit: dict[Drone, tuple[Zone, Zone]] = {}

        # Initialize all drones at start
        for drone in self.drones:
            self.drone_positions[drone] = graph.start_zone
            self.path_index[drone] = 0

    def run(self) -> None:
        """Run the simulation until all drones reach the goal."""

        while not self._all_drones_finished():
            self.turn += 1
            movements = []

            # Track moves for this turn
            moves_this_turn: list[tuple[Drone, Zone, Zone]] = []

            # Handle drones in transit
            for drone in list(self.in_transit.keys()):
                from_zone, to_zone = self.in_transit[drone]
                self._move_drone(drone, to_zone)
                movements.append(f"D{drone.id}-{to_zone.name}")
                del self.in_transit[drone]

            # Determine all potential moves
            for drone in self.drones:
                if self.drone_positions[drone] == self.graph.end_zone:
                    continue

                current_zone = self.drone_positions[drone]
                next_zone = self._get_next_zone(drone)
                moves_this_turn.append((drone, current_zone, next_zone))

            # Execute moves
            executed_moves = []
            for drone, from_zone, to_zone in moves_this_turn:
                if self._can_move_considering_moves(drone, from_zone, to_zone, executed_moves):
                    executed_moves.append((drone, from_zone, to_zone))

            # Apply all moves
            for drone, from_zone, to_zone in executed_moves:
                if to_zone.zone_type == "restricted":
                    self.in_transit[drone] = (from_zone, to_zone)
                    movements.append(f"D{drone.id}-{from_zone.name}-{to_zone.name}")
                else:
                    self._move_drone(drone, to_zone)
                    movements.append(f"D{drone.id}-{to_zone.name}")

            # Print movements with colors from zone metadata
            if movements:
                colored = []
                for m in movements:
                    zone_name = m.split('-')[-1]
                    zone = next((z for z in self.graph.zones if z.name == zone_name), None)
                    if zone and zone.color:
                        color_code = self._get_color_code(zone.color)
                        colored.append(f"{color_code}{m}\033[0m")
                    else:
                        colored.append(m)
                print(' '.join(colored))

        print(f"\n=== Simulation Complete in {self.turn} turns ===")

    def _get_color_code(self, color: str) -> str:
        """Get ANSI color code for a color name."""
        colors = {
            'red': '\033[91m', 'green': '\033[92m', 'yellow': '\033[93m', 'blue': '\033[94m',
            'cyan': '\033[96m', 'magenta': '\033[95m', 'gray': '\033[90m', 'white': '\033[97m',
            'orange': '\033[38;5;208m', 'purple': '\033[95m', 'violet': '\033[35m',
            'lime': '\033[92m', 'gold': '\033[93m', 'brown': '\033[38;5;130m',
            'crimson': '\033[38;5;160m', 'darkred': '\033[31m', 'maroon': '\033[38;5;52m',
            'black': '\033[30m', 'rainbow': '\033[96m'
        }
        return colors.get(color.lower(), '')

    def _get_next_zone(self, drone: Drone) -> Zone | None:
        """Get the next zone in the drone's path."""
        current_index = self.path_index[drone]
        path = self.paths[drone.id - 1]
        return path[current_index + 1]

    def _can_move_considering_moves(
        self,
        drone: Drone,
        from_zone: Zone,
        to_zone: Zone,
        executed_moves: list[tuple[Drone, Zone, Zone]]
    ) -> bool:
        """Check if move is valid."""
        if to_zone.is_blocked():
            return False

        if to_zone == self.graph.end_zone:
            return self._check_connection_capacity(from_zone, to_zone, executed_moves)

        current_in_dest = sum(
            1 for d in self.drones
            if self.drone_positions[d] == to_zone and d not in self.in_transit
        )

        for moved_drone, moved_from, moved_to in executed_moves:
            if moved_from == to_zone:
                current_in_dest -= 1
            if moved_to == to_zone:
                current_in_dest += 1

        if current_in_dest >= to_zone.max_drones:
            return False

        return self._check_connection_capacity(from_zone, to_zone, executed_moves)

    def _check_connection_capacity(
        self,
        from_zone: Zone,
        to_zone: Zone,
        executed_moves: list[tuple[Drone, Zone, Zone]]
    ) -> bool:
        """Check if connection has capacity."""
        connection = self.graph.get_connection(from_zone, to_zone)

        using_connection = 0
        # Count how many drone are already using the conection between A-B
        for moved_drone, moved_from, moved_to in executed_moves:
            if (moved_from == from_zone and moved_to == to_zone) or \
               (moved_from == to_zone and moved_to == from_zone):
                using_connection += 1

        return using_connection < connection.max_link_capacity

    def _move_drone(self, drone: Drone, next_zone: Zone) -> None:
        """Move drone to next zone."""
        self.drone_positions[drone] = next_zone
        self.path_index[drone] += 1

    def _all_drones_finished(self) -> bool:
        """Check if all drones have reached the goal."""
        for drone in self.drones:
            if self.drone_positions[drone] != self.graph.end_zone:
                return False
        return True
