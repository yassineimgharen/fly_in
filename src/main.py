from parser import parse_file
from models import Graph
from pathfinder import Pathfinder
from simulator import Simulator


def test_map(map_file: str, target_turns: int) -> None:
    """Test a map and compare against target."""
    print(f"\n{'='*70}")
    print(f"Testing: {map_file}")
    print(f"Target: ≤ {target_turns} turns")
    print('='*70)

    nb_drones, zones, connections, start_zone, end_zone = parse_file(map_file)
    graph = Graph(nb_drones, zones, connections, start_zone, end_zone)

    pathfinder = Pathfinder(graph)
    paths = pathfinder.find_multiple_paths(graph.nb_drones)

    unique_paths = len(set(tuple(z.name for z in p) for p in paths))
    print(f"Drones: {graph.nb_drones}")

    simulator = Simulator(graph, paths)
    simulator.run()

    # Check if we met the target
    if simulator.turn <= target_turns:
        print(f"✅ SUCCESS: {simulator.turn} turns (target: ≤{target_turns})")
    else:
        print(f"❌ FAILED: {simulator.turn} turns (target: ≤{target_turns})")


if __name__ == "__main__":
    # Easy maps
    # print("\n### EASY MAPS ###")
    # test_map("maps/easy/01_linear_path.txt", 6)
    # test_map("maps/easy/02_simple_fork.txt", 6)
    # test_map("maps/easy/03_basic_capacity.txt", 8)

    # # Medium maps
    # print("\n### MEDIUM MAPS ###")
    # test_map("maps/medium/01_dead_end_trap.txt", 15)
    # test_map("maps/medium/02_circular_loop.txt", 20)
    # test_map("maps/medium/03_priority_puzzle.txt", 12)

    # # Hard maps
    # print("\n### HARD MAPS ###")
    # test_map("maps/hard/01_maze_nightmare.txt", 45)
    # test_map("maps/hard/02_capacity_hell.txt", 60)
    test_map("test.txt", 5)
