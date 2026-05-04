import sys
from parser import parse_file
from models import Graph
from pathfinder import Pathfinder
from simulator import Simulator


def main() -> None:
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python main.py <map_file>")
        sys.exit(1)

    map_file = sys.argv[1]

    nb_drones, zones, connections, start_zone, end_zone = parse_file(map_file)
    graph = Graph(nb_drones, zones, connections, start_zone, end_zone)

    pathfinder = Pathfinder(graph)
    paths = pathfinder.find_multiple_paths(graph.nb_drones)

    simulator = Simulator(graph, paths)
    simulator.run()


if __name__ == "__main__":
    main()
